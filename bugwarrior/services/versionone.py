from twiggy import log
import v1pysdk

from bugwarrior.services import IssueService


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
        issues = list(self.v1.Story.where(Owners=userId, IsClosed='false').select('Name', 'Number', 'Team'))
        log.debug("Found issues: %s" % str(issues))

        return [{
            "description": self.description(
                issue.Name, issue.url,
                int(issue.Number.split('-')[-1]), cls="issue",
                ),
            "project": getattr(issue.Team, 'Name', 'uncategorized'),
            "priority": self.default_priority,
        } for issue in issues]


    def get_owner(self, issue):
        """ Override this for filtering on tickets """
        raise NotImplementedError()
