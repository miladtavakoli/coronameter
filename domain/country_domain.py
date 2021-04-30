from datetime import datetime


class CountryDomain(object):
    def __init__(self, country=None, wo_link=None, population=None,
                 created_at=datetime.now(),
                 updated_at=datetime.now(),
                 _id=None, flag=None):
        self._id = _id
        self.country = country
        self.wo_link = wo_link
        self.population = population
        self.flag = flag
        self.created_at = created_at
        self.updated_at = updated_at
        self._validate_input()

    @classmethod
    def from_dict(cls, input_dict):
        return CountryDomain(
            _id=input_dict.get("_id"),
            country=input_dict.get("country"),
            flag=input_dict.get("flag"),
            wo_link=input_dict.get("wo_link"),
            population=input_dict.get("population"),
            created_at=input_dict.get("created_at"),
            updated_at=input_dict.get("updated_at"),
        )

    def to_dict(self):
        result = {
            "_id": self._id,
            "country": self.country,
            "wo_link": self.wo_link,
            "population": self.population,
            "flag": self.flag,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }

        return {key: value for key, value in result.items() if value is not None}

    @classmethod
    def from_list_dict(cls, input_list):
        return [CountryDomain.from_dict(res) for res in input_list]

    @classmethod
    def to_list_dict(cls, input_list):
        return [CountryDomain.to_dict(res) for res in input_list]

    def _validate_input(self):
        if self.created_at is None:
            self.created_at = datetime.now()

        if self.updated_at is None:
            self.updated_at = datetime.now()
