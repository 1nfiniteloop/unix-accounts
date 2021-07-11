from abc import ABC, abstractmethod

from group import UnixGroup


class UnixGroupMemberStorage(ABC):

    @abstractmethod
    def add_member(self, user: str, group: str) -> UnixGroup:
        pass

    @abstractmethod
    def delete_member(self, user: str, group: str) -> UnixGroup:
        pass
