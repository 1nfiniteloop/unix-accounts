import sqlalchemy.exc
import sqlalchemy.event
from sqlalchemy.orm.query import Query
from sqlalchemy.orm.session import Session
from sqlalchemy.orm import (
    joinedload
)

from .db import Database
from .schema import SchemaBase



class DatabaseApi:

    def __init__(self, database: Database):
        self._database = database

    @property
    def _session(self) -> Session:
        return self._database.session

    def _query(self, cls, filters=(), preload=()) -> Query:
        query = self._session.query(cls).options(joinedload(rel) for rel in preload)
        if filters:
            query = query.filter(*filters)
        return query

    def _commit(self):
        try:
            self._session.commit()
        except sqlalchemy.exc.DatabaseError:
            self._session.rollback()
            raise

    def get(self, cls, filters: tuple=(), preload: tuple=()) -> list:
        return self._query(cls, filters, preload).all()

    def get_one(self, cls, filters: tuple=(), preload: tuple=()):
        return self._query(cls, filters, preload).one()

    def add(self, item: SchemaBase):
        self._session.add(item)
        self._commit()

    def add_all(self, items: list):
        self._session.add_all(items)
        self._commit()

    # bulk updates: https://docs.sqlalchemy.org/en/latest/orm/query.html?highlight=update#sqlalchemy.orm.query.Query.update
    # items_updated = self._query.filter(selector.filter).update(...)
    def update(self):
        self._commit()

    def delete(self, cls, filters: tuple=()) -> bool:
        rows = self._query(cls, filters).delete()
        self._commit()
        return rows > 0

    def exists(self, cls, filters: tuple=()) -> bool:
        rows = self._query(cls, filters).count()
        return rows > 0
