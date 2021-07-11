from typing import Tuple

from group import UnixGroup


class UnixUser:

    def __init__(self, name: str, uid: int = None, group: UnixGroup = None, gecos = None, home_dir: str = None, shell: str = None, group_membership: Tuple[str] = ()):
        self._name = name
        self._uid = uid
        self._group = group
        self._gecos = gecos
        self._home_dir = home_dir
        self._shell = shell
        self._group_membership = group_membership

    @property
    def name(self) -> str:
        return self._name

    @property
    def uid(self) -> int:
        return self._uid

    @property
    def group(self) -> UnixGroup:
        return self._group

    @property
    def gecos(self) -> str:
        return self._gecos

    @property
    def home_dir(self) -> str:
        return self._home_dir

    @property
    def shell(self) -> str:
        return self._shell

    @property
    def group_membership(self) -> Tuple[str]:
        return self._group_membership
