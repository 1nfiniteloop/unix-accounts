from typing import List
import sqlalchemy.exc

from group import UnixGroup
from error import (
    AlreadyExist,
    DoesNotExist,
    NotPossible
)
from storage.groups import UnixGroupStorage

from .sqlite_api import (
    Database,
    DatabaseApi
)
from .group_schema import (
    Group,
    GroupId
)
from .group_fmt import fmt_group


class UnixGroupStorageSqlite(UnixGroupStorage):

    def __init__(self, db: Database):
        self._db = DatabaseApi(db)

    def add(self, name: str, gid: int = None) -> UnixGroup:
        grp = Group()
        grp.name = name
        grp.group_id = GroupId(id=gid)
        try:
            self._db.add(grp)
        except sqlalchemy.exc.IntegrityError:
            if gid:
                msg = "Group \"{name}\" or gid {gid} is not unique".format(name=name, gid=gid)
            else:
                msg = "Group \"{name}\" is not unique".format(name=name)
            raise AlreadyExist(msg)
        return fmt_group(grp)

    def update_id(self, name: str, new_id: int) -> UnixGroup:
        try:
            group = self._try_update_id(name, new_id)
            return fmt_group(group)
        except sqlalchemy.exc.IntegrityError:
            raise AlreadyExist("Group id {new_gid} already exist".format(new_gid=new_id))
        except sqlalchemy.exc.NoResultFound:
            raise DoesNotExist("Group {name} does not exist".format(name=name))

    def _try_update_id(self, name: str, new_id: int) -> Group:
        group = self._db.get_one(Group, filters=(Group.name == name,))
        group.group_id.id = new_id
        self._db.update()
        return group

    def update_name(self, name: str, new_name: str) -> UnixGroup:
        try:
            group = self._try_update_name(name, new_name)
            return fmt_group(group)
        except sqlalchemy.exc.IntegrityError:
            raise AlreadyExist("Group {new_name} already exist".format(new_name=new_name))
        except sqlalchemy.exc.NoResultFound:
            raise DoesNotExist("Group {name} does not exist".format(name=name))

    def _try_update_name(self, name: str, new_name: str) -> Group:
        group = self._db.get_one(Group, filters=(Group.name == name,))
        group.name = new_name
        self._db.update()
        return group

    def delete(self, name: str):
        try:
            group = self._db.get_one(Group, filters=(Group.name == name,))
            self._db.delete(GroupId, filters=(GroupId.id == group.id,))
        except sqlalchemy.exc.IntegrityError:
            raise NotPossible("Group {name} can't be deleted because it's still bound to a user".format(name=name))
        except sqlalchemy.exc.NoResultFound:
            raise DoesNotExist("Group {name} does not exist".format(name=name))

    def get_by_id(self, gid: int) -> UnixGroup:
        try:
            group = self._db.get_one(Group, filters=(Group.id == gid,))
            return fmt_group(group)
        except sqlalchemy.exc.NoResultFound:
            raise DoesNotExist("Group with id {gid} does not exist".format(gid=gid))

    def get_by_name(self, name: str) -> UnixGroup:
        try:
            group = self._db.get_one(Group, filters=(Group.name == name,))
            return fmt_group(group)
        except sqlalchemy.exc.NoResultFound:
            raise DoesNotExist("Group {name} does not exist".format(name=name))

    def get_all(self) -> List[UnixGroup]:
        groups = self._db.get(Group)
        return [fmt_group(grp) for grp in groups]
