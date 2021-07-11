from typing import (
    List
)
from abc import ABC, abstractmethod

from group import UnixGroup


class UnixGroupStorage(ABC):

    @abstractmethod
    def add(self, name: str, gid: int=None) -> UnixGroup:
        pass

    @abstractmethod
    def update_id(self, name: str, new_id: int) -> UnixGroup:
        pass

    @abstractmethod
    def update_name(self, name: str, new_name: str) -> UnixGroup:
        pass

    @abstractmethod
    def delete(self, name: str):
        pass

    @abstractmethod
    def get_by_id(self, gid: int) -> UnixGroup:
        pass

    @abstractmethod
    def get_by_name(self, name: str) -> UnixGroup:
        pass

    @abstractmethod
    def get_all(self) -> List[UnixGroup]:
        pass
