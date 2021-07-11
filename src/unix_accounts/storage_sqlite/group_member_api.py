import sqlalchemy.exc

from error import (
    AlreadyExist,
    DoesNotExist
)
from group import UnixGroup
from storage import UnixGroupMemberStorage

from .group_schema import Group
from .group_fmt import fmt_group
from .user_schema import User
from .sqlite_api import (
    Database,
    DatabaseApi
)


class UnixGroupMemberStorageSqlite(UnixGroupMemberStorage):

    def __init__(self, db: Database):
        self._db = DatabaseApi(db)

    def add_member(self, user: str, group: str) -> UnixGroup:
        group = self._try_add_member(*self._try_load_member(user, group))
        return fmt_group(group)

    def _try_add_member(self, user: User, group: Group) -> Group:
        if user in group.user_membership:
            raise AlreadyExist("User {user} is already member of {grp}".format(user=user.name, grp=group.name))
        else:
            group.user_membership.append(user)
            self._db.update()
        return group

    def _try_load_member(self, user: str, group: str):
        try:
            group = self._db.get_one(Group, filters=(Group.name == group,))
        except sqlalchemy.exc.NoResultFound:
            raise DoesNotExist("Group {grp} does not exist".format(grp=group))
        try:
            user = self._db.get_one(User, filters=(User.name == user,))
        except sqlalchemy.exc.NoResultFound:
            raise DoesNotExist("User {user} does not exist".format(user=user))
        return user, group

    def delete_member(self, user: str, group: str) -> UnixGroup:
        group = self._try_delete_member(*self._try_load_member(user, group))
        return fmt_group(group)

    def _try_delete_member(self, user: User, group: Group) -> Group:
        if user in group.user_membership:
            group.user_membership.remove(user)
            self._db.update()
        else:
            raise DoesNotExist("User {user} is not a member of {grp}".format(user=user.name, grp=group.name))
        return group
