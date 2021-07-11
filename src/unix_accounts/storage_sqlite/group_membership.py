from sqlalchemy import (
    Column,
    ForeignKey,
    String,
)

from .schema_base import SchemaBase


class GroupMembership(SchemaBase):
    __tablename__ = "user_group_membership"
    user_name = Column(String(64), ForeignKey("user.name", onupdate="CASCADE", ondelete="CASCADE"), primary_key=True)
    group_name = Column(String(64), ForeignKey("group.name", onupdate="CASCADE", ondelete="CASCADE"), primary_key=True)
