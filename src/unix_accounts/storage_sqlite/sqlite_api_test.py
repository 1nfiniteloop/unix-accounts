import unittest
from sqlalchemy.ext.declarative import declarative_base
import sqlalchemy.exc
from sqlalchemy import (
    Column,
    Sequence,
    String,
    Integer,
)

from .schema import Schema
from .db_sqlite import SqliteDatabase
from .sqlite_api import DatabaseApi

Base = declarative_base()


class DatabaseSchema(Schema):

    """ Database model stub """

    def init(self, engine):
        Base.metadata.create_all(engine)


class User(Base):
    __tablename__ = "user"
    id = Column(Integer, Sequence('uid_sequence', minvalue=10000), primary_key=True)
    name = Column(String(64), unique=True, nullable=False)


class Group(Base):
    __tablename__ = "group"
    id = Column(Integer, Sequence('gid_sequence', minvalue=10000), primary_key=True)
    name = Column(String(64), unique=True, nullable=False)


class TestSqliteDatabaseApi(unittest.TestCase):

    """ Test against the real database """

    api = None
    db = None

    @classmethod
    def setUpClass(cls):
        model = DatabaseSchema()
        cls.db = SqliteDatabase(model)
        cls.api = DatabaseApi(cls.db)

    def tearDown(self):
        self.db.session.query(User).delete()
        self.db.session.query(Group).delete()

    def test_add_one(self):
        item = User(name="developer")
        self.api.add(item)
        # a primary key id is assigned when committed sucessfully.
        self.assertIsNotNone(item.id)

    def test_add_many(self):
        item_1 = User(name="developer")
        item_2 = Group(name="developer")
        self.api.add_all([item_1, item_2])
        # a primary key id is assigned when committed sucessfully.
        self.assertIsNotNone(item_1.id)
        self.assertIsNotNone(item_2.id)

    def test_get_one(self):
        item = User(name="developer")
        self.api.add(item)
        fetched_item = self.api.get_one(User)
        self.assertIs(item, fetched_item)

    def test_get_all(self):
        items = [User(name="developer-1"), User(name="developer-2")]
        self.api.add_all(items)
        fetched_items = self.api.get(User)
        self.assertCountEqual(items, fetched_items)

    def test_update(self):
        item = User(name="developer")
        self.api.add(item)
        item.name = "another-developer"
        self.api.update()
        self.assertCountEqual([], self.db.session.dirty)

    def test_delete(self):
        second_user_name = "second-developer"
        first, second = User(name="first-developer"), User(name=second_user_name)
        self.api.add(first)
        self.api.add(second)
        self.api.delete(User, filters=(User.name == second_user_name,))
        fetched = self.api.get(User, filters=(User.name == second_user_name,))
        self.assertCountEqual([], fetched)

    def test_auto_commit_rollback(self):
        items = [User(name="developer"), User(name="developer")]
        try:
            self.api.add_all(items)
        except sqlalchemy.exc.IntegrityError:
            # Expects to fail due to unique constraint for names.
            pass
        self.assertTrue(self.db.session.is_active)
