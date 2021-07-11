from crypt import crypt
import sqlalchemy.exc
from typing import List

from error import DoesNotExist
from storage import UnixPasswordStorage
from password import UnixPassword

from .sqlite_api import (
    Database,
    DatabaseApi
)
from .password_schema import Password


def _fmt_password(password: Password) -> UnixPassword:
    return UnixPassword(
        name=password.name,
        encrypted_password=password.encrypted_password,
        days_since_epoch_last_change=password.days_since_epoch_last_change,
        days_min=password.days_min,
        days_max=password.days_max,
        days_warn=password.days_warn,
        days_inactive=password.days_inactive,
        days_since_epoch_expires=password.days_since_epoch_expires
    )


class UnixPasswordStorageSqlite(UnixPasswordStorage):

    def __init__(self, db: Database):
        self._db = DatabaseApi(db)

    def update(self, user: str, new_password: str):
        self._try_update(user, new_password)

    def _try_update(self, name: str, new_password: str):
        try:
            password = self._db.get_one(Password, filters=(Password.name == name,))
            password.encrypted_password = crypt(new_password)
            self._db.update()
        except sqlalchemy.exc.NoResultFound:
            raise DoesNotExist("User {name} does not exist".format(name=name))

    def get_by_name(self, name: str) -> UnixPassword:
        try:
            password = self._db.get_one(Password, filters=(Password.name == name,))
            return _fmt_password(password)
        except sqlalchemy.exc.NoResultFound:
            raise DoesNotExist("User {name} does not exist".format(name=name))

    def get_all(self) -> List[UnixPassword]:
        passwords = self._db.get(Password)
        return [_fmt_password(sdw) for sdw in passwords]
