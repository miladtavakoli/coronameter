from repository.base import DailyRepoBase


class CaseReportRepository(DailyRepoBase):
    def __init__(self):
        self.collection = self.db['CaseDaily']

    def new_case_per_population(self, countries, from_date):
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
            {"$project": {"new_cases": 1,
                          "reported_at": 1,
                          "country": 1,
                          "pop": {"$divide": [{"$first": "$country_info.population"}, self.population_per_million]}}
             },
            {"$addFields": {
                "new_case_per_pop": {"$divide": ["$new_cases", "$pop"]}}
            },
            {"$sort": {"_id": -1}}
        ])
        return r
