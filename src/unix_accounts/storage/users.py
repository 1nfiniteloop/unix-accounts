from typing import (
    List
)
from abc import ABC, abstractmethod

from user import UnixUser


class UnixUserStorage(ABC):

    @abstractmethod
    def add(self, name: str, uid: int = None, gid: int = None, gecos: str = None, home_dir: str = None, shell: str = None) -> UnixUser:
        pass

    @abstractmethod
    def update_id(self, name: str, new_uid: int) -> UnixUser:
        pass

    @abstractmethod
    def update_gid(self, name: str, new_gid: int) -> UnixUser:
        pass

    @abstractmethod
    def update_name(self, name: str, new_name: str) -> UnixUser:
        pass

    @abstractmethod
    def update_gecos(self, name: str, new_gecos: str) -> UnixUser:
        pass

    @abstractmethod
    def update_home_dir(self, name: str, new_home_dir: str) -> UnixUser:
        pass

    @abstractmethod
    def update_shell(self, name: str, new_shell: str) -> UnixUser:
        pass

    @abstractmethod
    def delete(self, name: str):
        pass

    @abstractmethod
    def get_by_id(self, uid: int) -> UnixUser:
        pass

    @abstractmethod
    def get_by_name(self, name: str) -> UnixUser:
        pass

    @abstractmethod
    def get_all(self) -> List[UnixUser]:
        pass
