import sqlalchemy
from sqlalchemy.orm import (
    sessionmaker,
    scoped_session,
)
import sqlalchemy.event
import sqlalchemy.exc
from sqlalchemy.engine import Engine
from sqlalchemy.orm.session import Session

from error import InternalError
from .schema import Schema
from .db import Database


@sqlalchemy.event.listens_for(Engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    """ https://docs.sqlalchemy.org/en/latest/dialects/sqlite.html#foreign-key-support """
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()


class SqliteDatabase(Database):

    def __init__(self, model: Schema, db=":memory:", verbose=False):
        engine = sqlalchemy.create_engine("sqlite:///{db}".format(db=db), echo=verbose)
        self._session_maker = scoped_session(sessionmaker(bind=engine))
        try:
            model.init(engine)
        except sqlalchemy.exc.OperationalError as err:
            raise InternalError("{db}: {msg}".format(db=db, msg=err))

    @property
    def session(self) -> Session:
        return self._session_maker()
