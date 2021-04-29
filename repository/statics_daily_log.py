from repository.base import BaseDB


class StaticsRepository(BaseDB):
    def __init__(self):
        self.collection = self.db['DailyStatics']

    def insert_many(self, items : list):
        return self.collection.insert_many(items)

    def find_logged_bye_time(self, from_time, to_time):
        res = self.collection.aggregate([
            {"match": {"created_at": {"$gte": from_time, "$lte": to_time}}}
        ])
        return list(res)