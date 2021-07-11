from typing import List, Tuple
import sqlalchemy.exc
from sqlalchemy.sql.expression import func
from error import (
    DoesNotExist,
    AlreadyExist,
)
from storage import UnixUserStorage
from user import UnixUser

from .group_fmt import fmt_group
from .group_schema import (
    Group,
    GroupId
)
from .password_schema import Password
from .user_schema import (
    User,
    UserId
)
from .sqlite_api import (
    Database,
    DatabaseApi
)


def _fmt_group_members(groups: Tuple[User]) -> Tuple[str]:
    return tuple(group.name for group in groups)


def _fmt_user(user: User) -> UnixUser:
    return UnixUser(
        name=user.name,
        uid=user.id,
        group=fmt_group(user.group),
        gecos=user.gecos,
        home_dir=user.home_dir,
        shell=user.shell,
        group_membership=_fmt_group_members(user.group_membership)
    )


class UnixUserStorageSqlite(UnixUserStorage):

    def __init__(self, db: Database):
        self._db = DatabaseApi(db)

    @staticmethod
    def _default_home(user_name: str) -> str:
        return "/home/" + user_name

    def add(self, name: str, uid: int = None, gid: int = None, gecos: str = None, home_dir: str = None, shell: str = None) -> UnixUser:
        user = User()
        user.name = name
        user.user_id = UserId(id=uid)
        user.shell = shell
        user.gecos = gecos
        if home_dir:
            user.home_dir = home_dir
        else:
            user.home_dir = self._default_home(name)
        if gid:
            if self._db.exists(Group, filters=(Group.id == gid)):
                user.gid = gid
            else:
                raise DoesNotExist("Group id {gid} does not exist".format(gid=gid))
        else:
            user.group = self._try_add_group(name, uid)
        user.password = Password()
        user.password.name = name

        try:
            self._db.add(user)
        except sqlalchemy.exc.IntegrityError:
            if uid:
                msg = "User: \"{name}\" or uid: {uid} is not unique".format(name=name, uid=user.id)
            else:
                msg = "User: \"{name}\" is not unique".format(name=name)
            raise AlreadyExist(msg)
        return _fmt_user(user)

    def _try_add_group(self, name: str, gid: int) -> Group:
        # Try to favor uid == gid
        group = Group()
        group.name = name
        if not self._db.exists(Group, filters=(Group.id == gid,)):
            group.group_id = GroupId(id=gid)
        else:
            group.group_id = GroupId()
        return group

    def update_id(self, name: str, new_id: int) -> UnixUser:
        try:
            user = self._db.get_one(User, filters=(User.name == name,), preload=(User.user_id,))
            user.user_id.id = new_id
            self._db.update()
            return _fmt_user(user)
        except sqlalchemy.exc.NoResultFound:
            raise DoesNotExist("User id {name} does not exist".format(name=name))
        except sqlalchemy.exc.IntegrityError:
            raise AlreadyExist("User with id {uid} already exist".format(uid=new_id))

    def update_gid(self, name: str, new_gid: int) -> UnixUser:
        try:
            user = self._db.get_one(User, filters=(User.name == name,))
            user.gid = new_gid
            self._db.update()
            return _fmt_user(user)
        except sqlalchemy.exc.NoResultFound:
            raise DoesNotExist("User {name} does not exist".format(name=name))
        except sqlalchemy.exc.IntegrityError:
            raise DoesNotExist("Group id {gid} does not exist".format(gid=new_gid))

    def update_name(self, name: str, new_name: str) -> UnixUser:
        try:
            user = self._db.get_one(User, filters=(User.name == name,))
            user.name = new_name
            self._db.update()
            return _fmt_user(user)
        except sqlalchemy.exc.NoResultFound:
            raise DoesNotExist("User {name} does not exist".format(name=name))
        except sqlalchemy.exc.IntegrityError:
            raise AlreadyExist("User {name} already exist".format(name=new_name))

    def update_gecos(self, name: str, new_gecos: str) -> UnixUser:
        try:
            user = self._db.get_one(User, filters=(User.name == name,))
            user.gecos = new_gecos
            self._db.update()
            return _fmt_user(user)
        except sqlalchemy.exc.NoResultFound:
            raise DoesNotExist("User {name} does not exist".format(name=name))

    def update_home_dir(self, name: str, new_home_dir: str) -> UnixUser:
        try:
            user = self._db.get_one(User, filters=(User.name == name,))
            user.home_dir = new_home_dir
            self._db.update()
            return _fmt_user(user)
        except sqlalchemy.exc.NoResultFound:
            raise DoesNotExist("User {name} does not exist".format(name=name))

    def update_shell(self, name: str, new_shell: str) -> UnixUser:
        try:
            user = self._db.get_one(User, filters=(User.name == name,))
            user.shell = new_shell
            self._db.update()
            return _fmt_user(user)
        except sqlalchemy.exc.NoResultFound:
            raise DoesNotExist("User {name} does not exist".format(name=name))

    def delete(self, name: str) -> bool:
        try:
            user = self._db.get_one(User, filters=(User.name == name,))
            return self._db.delete(UserId, filters=(UserId.id == user.id,))
        except sqlalchemy.exc.NoResultFound:
            raise DoesNotExist("User {name} does not exist".format(name=name))

    def get_by_id(self, uid: int) -> UnixUser:
        try:
            user = self._db.get_one(User, filters=(User.id == uid,))
            return _fmt_user(user)
        except sqlalchemy.exc.NoResultFound:
            raise DoesNotExist("User with uid: {uid} does not exist".format(uid=uid))

    def get_by_name(self, name: str) -> UnixUser:
        try:
            user = self._db.get_one(User, filters=(User.name == name,))
            return _fmt_user(user)
        except sqlalchemy.exc.NoResultFound:
            raise DoesNotExist("User: {name} does not exist".format(name=name))

    def get_all(self) -> List[UnixUser]:
        users = self._db.get(User)
        return [_fmt_user(user) for user in users]
