from typing import Tuple

from group import UnixGroup
from .group_schema import Group
from .user_schema import User


def _fmt_user_members(users: Tuple[User]) -> Tuple[str]:
    return tuple(user.name for user in users)


def fmt_group(grp: Group) -> UnixGroup:
    return UnixGroup(
        grp.name,
        grp.id,
        _fmt_user_members(grp.user_membership)
    )
