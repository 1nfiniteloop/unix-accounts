from typing import Tuple


class UnixGroup:

    def __init__(self, name: str, id_: int, members: Tuple[str] = ()):
        self._name = name
        self._id = id_
        self._members = members

    @property
    def name(self) -> str:
        return self._name

    @property
    def id(self) -> int:
        return self._id

    @property
    def members(self) -> Tuple[str]:
        return self._members