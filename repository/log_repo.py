from repository.base import BaseDB
from domain.log_domain import Log


class CrawlerLogRepository(BaseDB):
    """
        crawl timing
    """

    def __init__(self):
        self.collection = self.db['log']

    def save(self, doc: Log):
        return self.collection.insert_one(doc.to_dict())

    def list(self):
        res = self.collection.find().sort([("_id", -1)])
        return [Log.from_dict(r) for r in list(res)]
