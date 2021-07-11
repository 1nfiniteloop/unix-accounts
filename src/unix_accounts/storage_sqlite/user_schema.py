from sqlalchemy.orm import relationship
from sqlalchemy import (
    Column,
    ForeignKey,
    Sequence,
    String,
    Integer,
    DateTime
)
from sqlalchemy.sql import func
from datetime import datetime

from .schema_base import SchemaBase
from .group_membership import GroupMembership


# sqlite don't support auto-increment on non-primary keys, thus id is a separate table
class UserId(SchemaBase):
    __tablename__ = "user_id"
    id = Column(Integer, Sequence('uid_sequence', minvalue=10000), primary_key=True)
    user = relationship("User", uselist=False, back_populates="user_id")


class User(SchemaBase):
    DEFAULT_SHELL = "/bin/bash"

    __tablename__ = "user"
    name = Column(String(64), primary_key=True, nullable=False, index=True)
    id = Column(Integer, ForeignKey('user_id.id', onupdate="CASCADE", ondelete="CASCADE"), nullable=False, unique=True)
    gecos = Column(String(128))
    home_dir = Column(String(256), nullable=False)
    shell = Column(String(32), default=DEFAULT_SHELL, nullable=False)
    gid = Column(Integer, ForeignKey('group.id', onupdate="CASCADE"), nullable=False, unique=True)
    created = Column(DateTime(timezone=True), server_default=func.now())
    modified = Column(DateTime(timezone=True), server_default=func.now(), onupdate=datetime.now)

    # object relation mappers:
    user_id = relationship("UserId", back_populates="user", uselist=False, cascade="all,delete-orphan", single_parent=True)
    group = relationship("Group", uselist=False)
    group_membership = relationship("Group", secondary=GroupMembership.__tablename__, back_populates="user_membership")
    password = relationship("Password", uselist=False)
