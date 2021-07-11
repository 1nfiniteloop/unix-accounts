from datetime import datetime
from sqlalchemy import (
    Column,
    ForeignKey,
    String,
    Integer,
)

from .schema_base import SchemaBase

EPOCH_TIME = datetime(1970, 1, 1)


def days_since_epoch():
    delta = datetime.now() - EPOCH_TIME
    return delta.days


class Password(SchemaBase):

    DEFAULT_PASSWD, DEFAULT_MIN, DEFAULT_MAX, DEFAULT_WARN = "*", 0, 99999, 7

    __tablename__ = "password"

    name = Column(String(64), ForeignKey('user.name', onupdate="CASCADE", ondelete="CASCADE"), primary_key=True, index=True)
    encrypted_password = Column(String(128), default=DEFAULT_PASSWD, nullable=False)
    days_since_epoch_last_change = Column(Integer, default=days_since_epoch, nullable=False)
    days_min = Column(Integer, default=DEFAULT_MIN, nullable=False)
    days_max = Column(Integer, default=DEFAULT_MAX, nullable=False)
    days_warn = Column(Integer, default=DEFAULT_WARN, nullable=False)
    days_inactive = Column(Integer)
    days_since_epoch_expires = Column(Integer)
