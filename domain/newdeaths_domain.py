from datetime import datetime


class NewDeathDomain(object):
    def __init__(self, country, new_deaths, _id=None,
                 reported_at=datetime.now(),
                 created_at=datetime.now(),
                 updated_at=datetime.now(),
                 ):
        self._id = _id
        self.country = country
        self.new_deaths = new_deaths
        self.reported_at = reported_at
        self.created_at = created_at
        self.updated_at = updated_at
        self._validate_input()

    @classmethod
    def from_dict(cls, input_dict):
        return NewDeathDomain(
            _id=input_dict.get("_id"),
            country=input_dict.get("country"),
            new_deaths=input_dict.get("new_deaths"),
            reported_at=input_dict.get("reported_at", datetime.now()),
            created_at=input_dict.get("created_at", datetime.now()),
            updated_at=input_dict.get("updated_at", datetime.now()),
        )

    def to_dict(self):
        result = {
            "_id": self._id,
            "country": self.country,
            "new_deaths": self.new_deaths,
            "reported_at": self.reported_at,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }

        return {key: value for key, value in result.items() if value is not None}

    @classmethod
    def from_list_of_dict(cls, input_list):
        return [NewDeathDomain.from_dict(res) for res in input_list]

    def _validate_input(self):
        if self.reported_at is None and isinstance(self.reported_at, str):
            self.reported_at = datetime.strptime(self.reported_at, "%b %d, %Y")
