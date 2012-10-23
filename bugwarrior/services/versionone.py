import time, calendar
from twiggy import log
import v1pysdk

from bugwarrior.services import IssueService

# TODO:
#   * update README

def parsedate(s):
    """ Return the given time (in a string of the form year-month-day)
        as  seconds since epoch.
    """
    return calendar.timegm(time.strptime(s, "%Y-%m-%d"))


class VersionOneService(IssueService):
    def __init__(self, *args, **kw):
        super(VersionOneService, self).__init__(*args, **kw)
        url = self.config.get(self.target, 'versionone.url')
        self.v1 = v1pysdk.V1Meta(
                address=url,
                instance='VersionOne',
                username=self.config.get(self.target, 'versionone.username'),
                password=self.config.get(self.target, 'versionone.password'),
                )

    def issues(self):
        """ Return the stories assigned to the user"""
        user = self.v1.Member.where(IsSelf='true').first()
        userId = "%s:%s" % (user.AssetType, user.Key)
        log.debug("Fetching tasks for versionOne user \"%s\", ID: %s" % (user.Name, userId))
        issues = list(self.v1.Story.where(Owners=userId, IsClosed='false').select('Name', 'Number', 'Team', 'Timebox'))
        if self.config.get(self.target, 'current_sprint'):
            issues = filter(self.is_current_sprint, issues)
        log.debug("Found %d issues." % len(issues))

        tasks = []
        for issue in issues:
            task = {
                    "description": self.description(
                                        issue.Name, issue.url,
                                        int(issue.Number.split('-')[-1]), cls="backlog",
                                    ),
                    "project": getattr(issue.Team, 'Name', 'uncategorized'),
                    "priority": self.default_priority,
                }

            due_date = self.get_due_date(issue)
            if due_date:
                task["due"] = due_date

            tasks.append(task)

        return tasks

    def is_current_sprint(self, issue):
        """ Return True if the given issue is assigned to the active sprint.
        """
        if not issue.Timebox:
            return False

        current_time = time.time()
        end_time = parsedate(issue.Timebox.EndDate)
        start_time = parsedate(issue.Timebox.BeginDate)
        return start_time < current_time < end_time

    def get_due_date(self, issue):
        """ Return the due date of the issue in a format usable by taskwarrior
        """
        if not issue.Timebox:
            return None

        return str(parsedate(issue.Timebox.EndDate))

    def get_owner(self, issue):
        """ Override this for filtering on tickets """
        raise NotImplementedError()
