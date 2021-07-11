from typing import (
    Tuple,
)

from terminaltables import AsciiTable
from group import UnixGroup


def fmt_members(members: Tuple[str]):
    return ",".join(members)


def fmt_groups(groups: Tuple[UnixGroup]):
    return list([grp.name, grp.id, fmt_members(grp.members)] for grp in groups)


class GroupsAsciiTable:

    def __init__(self, groups: Tuple[UnixGroup]):
        self._groups = fmt_groups(groups)

    def __str__(self):
        HEADER = ("Group name", "Id", "User membership")
        data = [HEADER]
        data.extend(self._groups)
        ascii_table = AsciiTable(data)
        return ascii_table.table
