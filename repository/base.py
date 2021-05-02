from datetime import datetime

from repository.connection import MongoConnection


class BaseDB(MongoConnection):

    def _rebuild_before_insert(self, input_item, country=None, many=False):
        if many:
            for item in input_item:
                self._append_required_fields(item, country)
        else:
            self._append_required_fields(input_item, country)

        return input_item

    @staticmethod
    def _append_required_fields(item, country=None):
        item["created_at"] = datetime.now()
        item["updated_at"] = datetime.now()
        if item.get('reported_at') is not None and isinstance(item['reported_at'], str):
            item['reported_at'] = datetime.strptime(item['reported_at'], "%b %d, %Y")
        if country is not None:
            item['country'] = country

        return item


class DailyRepoBase(BaseDB):
    collection = None
    field_name = None
    population_per_million = 1_000_000

    def insert_many(self, items):
        return self.collection.insert_many(items)

    def insert_one(self, item):
        return self.collection.insert_one(item)

    def update_one_value(self, _id, new_value):
        return self.collection.update_one({"_id": _id}, {"$set": new_value})

    def total_value_by(self, country):
        return self.collection.aggregate([
            {"$match": {"country": country}},
            {
                "$group": {
                    "_id": {"country": country},
                    "total_value": {"$sum": f"${self.field_name}"},
                    "last_value": {"$last": "$reported_at"}
                }
            },
        ])

    def get_last_report(self, country):
        res = self.collection.aggregate([
            {"$match": {"country": country}},
            {"$sort": {"reported_at": -1}},
            {"$limit": 1}
        ])
        return list(res)

    def get_country_days_ago(self, country, from_day):
        res = self.collection.find({"country": country, "reported_at": {"$gte": from_day}})
        return list(res)

