from datetime import datetime


class StaticsDomain(object):
    def __init__(self, country, new_cases, new_deaths, new_recovered, population,
                 created_at=datetime.now(),
                 updated_at=datetime.now(),
                 _id=None
                 ):
        self._id = _id
        self.country = country
        self.new_cases = new_cases
        self.new_deaths = new_deaths
        self.new_recovered = new_recovered
        self.population = population
        self.created_at = created_at
        self.updated_at = updated_at
        self._validate_input()

    @classmethod
    def from_dict(cls, input_dict):
        return StaticsDomain(
            _id=input_dict.get("_id"),
            country=input_dict.get("country"),
            new_cases=input_dict.get("new_cases"),
            new_deaths=input_dict.get("new_deaths"),
            new_recovered=input_dict.get("new_recovered"),
            population=input_dict.get("population"),
            created_at=input_dict.get("created_at"),
            updated_at=input_dict.get("updated_at"),
        )

    def to_dict(self):
        result = {
            "_id": self._id,
            "country": self.country,
            "new_cases": self.new_cases,
            "new_deaths": self.new_deaths,
            "new_recovered": self.new_recovered,
            "population": self.population,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }

        return {key: value for key, value in result.items() if value is not None}

    @classmethod
    def from_list_dict(cls, input_list):
        # list of dicts to list of objects
        return [StaticsDomain.from_dict(res) for res in input_list]

    @classmethod
    def to_list_dict(cls, input_list):
        # list of objects to list of dicts
        return [StaticsDomain.to_dict(res) for res in input_list]

    def _validate_input(self):
        if self.created_at is None:
            self.created_at = datetime.now()

        if self.updated_at is None:
            self.updated_at = datetime.now()
