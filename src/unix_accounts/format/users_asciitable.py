from typing import (
    Tuple,
)

from terminaltables import AsciiTable
from user import UnixUser


def _fmt_members(members: Tuple[str]):
    return ",".join(members)


def _fmt_users(users: Tuple[UnixUser]):
    return list([user.name, user.uid, user.group.name, user.gecos or "", user.home_dir, user.shell, _fmt_members(user.group_membership)] for user in users)


class UsersAsciiTable:

    def __init__(self, users: Tuple[UnixUser]):
        self._users = _fmt_users(users)

    def __str__(self):
        HEADER = ("User name", "Id", "Group", "Gecos", "Home dir", "Shell", "Group membership")
        data = [HEADER]
        data.extend(self._users)
        ascii_table = AsciiTable(data)
        return ascii_table.table
