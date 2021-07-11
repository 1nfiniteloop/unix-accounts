from .db_sqlite import (
    SqliteDatabase,
)

from storage import (
    UnixGroupStorage,
    UnixUserStorage,
    UnixGroupMemberStorage,
    UnixPasswordStorage
)

from .schema import UnixAccountSchema
from .group_api import UnixGroupStorageSqlite
from .user_api import UnixUserStorageSqlite
from .group_member_api import UnixGroupMemberStorageSqlite
from .password_api import UnixPasswordStorageSqlite


class Api:

    def __init__(self, database_name: str, verbose: bool = False):
        self._database = SqliteDatabase(
            UnixAccountSchema(),
            database_name,
            verbose
        )

    @property
    def groups(self) -> UnixGroupStorage:
        return UnixGroupStorageSqlite(self._database)

    @property
    def users(self) -> UnixUserStorage:
        return UnixUserStorageSqlite(self._database)

    @property
    def group_members(self) -> UnixGroupMemberStorage:
        return UnixGroupMemberStorageSqlite(self._database)

    @property
    def password(self) -> UnixPasswordStorage:
        return UnixPasswordStorageSqlite(self._database)
