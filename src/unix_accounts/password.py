
class UnixPassword:

    def __init__(
            self,
            name: str,
            encrypted_password: str,
            days_since_epoch_last_change: int,
            days_min: int,
            days_max: int,
            days_warn: int,
            days_inactive: int,
            days_since_epoch_expires: int
    ):
        self._name = name
        self._encrypted_password = encrypted_password
        self._days_since_epoch_last_change = days_since_epoch_last_change
        self._days_min = days_min
        self._days_max = days_max
        self._days_warn = days_warn
        self._days_inactive = days_inactive
        self._days_since_epoch_expires = days_since_epoch_expires

    @property
    def name(self) -> str:
        return self._name

    @property
    def encrypted_password(self):
        return self._encrypted_password

    @property
    def days_since_epoch_last_change(self):
        return  self._days_since_epoch_last_change

    @property
    def days_min(self):
        return self._days_min

    @property
    def days_max(self):
        return self._days_max

    @property
    def days_warn(self):
        return self._days_warn

    @property
    def days_inactive(self):
        return self._days_inactive

    @property
    def days_since_epoch_expires(self):
        return self._days_since_epoch_expires
