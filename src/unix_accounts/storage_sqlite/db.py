from abc import (
    ABC,
    abstractmethod
)

from sqlalchemy.orm.session import Session


class Database(ABC):

    """ Interface for a database """

    @property
    @abstractmethod
    def session(self) -> Session:
        pass
