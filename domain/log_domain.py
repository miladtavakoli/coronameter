class Log(object):
    def __init__(self, command, count, status, started_at, ends_at, _id=None):
        self._id = _id
        self.command = command
        self.count = count
        self.started_at = started_at
        self.status = status
        self.ends_at = ends_at

    @classmethod
    def from_dict(cls, input_dict):
        return Log(
            _id=input_dict.get('_id', None),
            command=input_dict.get('command'),
            count=input_dict.get('count', 0),
            status=input_dict.get('status', 200),
            started_at=input_dict.get('started_at'),
            ends_at=input_dict.get('ends_at'),
        )

    def to_dict(self):
        result = {
            "_id": self._id,
            "command": self.command,
            "count": self.count,
            "started_at": self.started_at,
            "status": self.status,
            "ends_at": self.ends_at,
        }
        return {key: value for key, value in result.items() if value is not None}
