class LogList:
    def __init__(self, repo):
        self.repo = repo

    def execute(self):
        res = self.repo.list()
        return [r.to_dict() for r in res]
