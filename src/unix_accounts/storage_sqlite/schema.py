from abc import (
    ABC,
    abstractmethod
)
from sqlalchemy.engine import Engine

# exposes the model
# since they have internal relationships they need to be initialized in a specific order
from .schema_base import SchemaBase
from .group_membership import GroupMembership
from .group_schema import (
    Group,
    GroupId
)
from .user_schema import (
    User,
    UserId
)
from .password_schema import Password


class Schema(ABC):

    @abstractmethod
    def init(self, engine):
        pass


class UnixAccountSchema(Schema):

    """ initialize empty database with tables and relations """

    def init(self, engine: Engine):
        SchemaBase.metadata.create_all(engine)
