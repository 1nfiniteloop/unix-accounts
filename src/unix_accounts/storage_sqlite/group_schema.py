from datetime import datetime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from sqlalchemy import (
    Column,
    ForeignKey,
    Sequence,
    String,
    Integer,
    DateTime
)

from .schema_base import SchemaBase
from .group_membership import GroupMembership


# sqlite don't support auto-increment on non-primary keys, thus id is a separate table
class GroupId(SchemaBase):
    __tablename__ = "group_id"
    id = Column(Integer, Sequence('uid_sequence', minvalue=10000), primary_key=True)
    group = relationship("Group", uselist=False, back_populates="group_id")


class Group(SchemaBase):
    __tablename__ = "group"
    name = Column(String(64), unique=True, nullable=False, index=True, primary_key=True)
    id = Column(Integer, ForeignKey('group_id.id', onupdate="CASCADE", ondelete="CASCADE"), nullable=False, unique=True)
    created = Column(DateTime(timezone=True), server_default=func.now())
    modified = Column(DateTime(timezone=True), server_default=func.now(), onupdate=datetime.now)

    # object relation mappers:
    group_id = relationship("GroupId", back_populates="group", uselist=False, cascade="all,delete-orphan", single_parent=True)
    user_membership = relationship("User", secondary=GroupMembership.__tablename__, back_populates="group_membership")
