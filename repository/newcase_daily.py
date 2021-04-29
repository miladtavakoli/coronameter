from repository.base import DailyRepoBase


class CaseReportRepository(DailyRepoBase):
    def __init__(self):
        self.collection = self.db['CaseDaily']
