from datetime import datetime

from repository.base import DailyRepoBase


class DeathReportRepository(DailyRepoBase):
    def __init__(self):
        self.collection = self.db['DeathDaily']

    def death_per_population(self, countries: list, from_date: datetime):
        r = self.collection.aggregate([
            {"$match": {
                "country": {"$in": countries},
                "reported_at": {"$gte": from_date}}
            },
            {"$lookup": {
                "from": "Countries",
                "localField": "country",
                "foreignField": "country",
                "as": "country_info"}
            },
            {"$project": {"new_deaths": 1,
                          "reported_at": 1,
                          "country": 1,
                          "pop": {"$divide": [{"$first": "$country_info.population"}, self.population_per_million]}}
             },
            {"$addFields": {
                "new_deaths_per_pop": {"$divide": ["$new_deaths", "$pop"]}
            }},
            {"$sort": {"_id": -1}}

        ])
        return list(r)
