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
        issues = user.OwnedWorkitems

        return [{
            "description": self.description(
                issue.Name, issue.url,
                issue.Number, cls="issue",
                ),
            "project": issue.Team.Name,
            "priority": self.default_priority,
        } for tag, issue in issues]


    def get_owner(self, issue):
        """ Override this for filtering on tickets """
        raise NotImplementedError()
