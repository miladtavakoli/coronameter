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
        self._set_default_datetime()

    @classmethod
    def from_dict(cls, input_dict):
        return NewDeathDomain(
            _id=input_dict.get("_id"),
            country=input_dict.get("country"),
            new_deaths=input_dict.get("new_deaths"),
            reported_at=input_dict.get("reported_at"),
            created_at=input_dict.get("created_at"),
            updated_at=input_dict.get("updated_at"),
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
    def from_list_dict(cls, input_list):
        """Converts list of dicts to list of objects"""
        return [NewDeathDomain.from_dict(res) for res in input_list]

    @classmethod
    def to_list_dict(cls, input_list):
        """Converts list of objects to list of dicts"""
        return [NewDeathDomain.to_dict(res) for res in input_list]

    def _set_default_datetime(self):
        if self.reported_at is not None and isinstance(self.reported_at, str):
            self.reported_at = datetime.strptime(self.reported_at, "%b %d, %Y")

        if self.created_at is None:
            self.created_at = datetime.now()

        if self.updated_at is None:
            self.updated_at = datetime.now()
