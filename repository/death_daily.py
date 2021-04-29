from repository.base import DailyRepoBase


class DeathReportRepository(DailyRepoBase):
    def __init__(self):
        self.collection = self.db['DeathDaily']
