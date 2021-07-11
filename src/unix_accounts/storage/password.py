from abc import ABC, abstractmethod
from typing import List

from password import UnixPassword


class UnixPasswordStorage(ABC):

    @abstractmethod
    def update(self, user: str, new_password: str):
        pass

    @abstractmethod
    def get_by_name(self, name: str) -> UnixPassword:
        pass

    @abstractmethod
    def get_all(self) -> List[UnixPassword]:
        pass
