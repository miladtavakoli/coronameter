from domain.country_domain import CountryDomain
from repository.base import BaseDB


class CountriesRepository(BaseDB):
    def __init__(self):
        self.collection = self.db['Countries']

    def find_one(self, query: dict):
        res = self.collection.find_one(query, {"country": 1, "population": 1, "updated_at": 1, "_id": 0})
        return res

    def country_list(self, query=None):
        if query is None:
            query = {}
        res = list(self.collection.find(query, {"_id": "$country"}))
        return [CountryDomain.from_dict(r) for r in res]

    def update_one(self, find_query: dict, set_: dict, upsert=True):
        return self.collection.update(find_query, {"$set": set_}, upsert)

    def insert_one(self, insert_doc: dict):
        return self.collection.insert_one(insert_doc)

    def find_countries(self, countries):
        return list(self.collection.find({"country": {"$in": countries}}))
