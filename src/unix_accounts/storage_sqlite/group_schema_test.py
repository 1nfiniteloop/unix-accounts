import unittest
import datetime
import sqlalchemy.exc
import sqlalchemy.orm.exc


from .db_sqlite import SqliteDatabase
from .schema import (
    UnixAccountSchema,
    Group,
    GroupId
)


class Defaults:
    group_name = "group"
    group_id = 10000


def default_group():
    return Group(
        name=Defaults.group_name,
        group_id=GroupId()
    )


class GroupSchemaTest(unittest.TestCase):

    def setUp(self):
        self.database = SqliteDatabase(
            UnixAccountSchema(),
            ":memory:",
            # verbose=True
        )

    def test_add_group(self):
        group = default_group()
        self.database.session.add(group)
        self.database.session.commit()
        fetched_group = self.database.session.query(Group).one()
        self.assertEqual(group, fetched_group)

    # delete GroupId and cascade delete Group, from database layer
    def test_db_remove_group_and_its_group_id(self):
        group = default_group()
        group.group_id.id = Defaults.group_id
        self.database.session.add(group)
        self.database.session.commit()
        group = self.database.session.query(Group).filter(Group.name == Defaults.group_name).one()
        self.database.session.query(GroupId).filter(GroupId.id == group.id).delete()
        with self.assertRaises(sqlalchemy.orm.exc.NoResultFound):
            _ = self.database.session.query(GroupId).filter(GroupId.id == Defaults.group_id).one()

    # delete Group and GroupId, from object relation mappers
    def test_orm_remove_group_and_its_group_id(self):
        group = default_group()
        group.group_id.id = Defaults.group_id
        self.database.session.add(group)
        self.database.session.commit()
        group = self.database.session.query(Group).filter(Group.name == Defaults.group_name).one()
        self.database.session.delete(group)
        with self.assertRaises(sqlalchemy.orm.exc.NoResultFound):
            _ = self.database.session.query(GroupId).filter(GroupId.id == Defaults.group_id).one()

    def test_update_group_and_its_group_id(self):
        group = default_group()
        group.group_id.id = 10000
        self.database.session.add(group)
        self.database.session.commit()
        group.group_id.id = 10001
        self.database.session.commit()
        with self.assertRaises(sqlalchemy.orm.exc.NoResultFound):
            _ = self.database.session.query(GroupId).filter(GroupId.id == 10000).one()

    def test_name_required(self):
        group = default_group()
        group.name = None
        self.database.session.add(group)
        with self.assertRaisesRegex(sqlalchemy.exc.IntegrityError, "group.name"):
            self.database.session.commit()

    def test_name_unique(self):
        first = default_group()
        second = default_group()
        self.database.session.add_all((first, second))
        with self.assertRaisesRegex(sqlalchemy.exc.IntegrityError, "group.name"):
            self.database.session.commit()

    def test_uid_auto_increment(self):
        first = default_group()
        first.group_id.id = 10000
        second = default_group()
        second.name = "second-group"
        self.database.session.add_all((first, second))
        self.database.session.commit()
        self.assertEqual(first.id + 1, second.id)

    def test_date_created_default(self):
        group = default_group()
        self.database.session.add(group)
        self.database.session.commit()
        self.assertLess(datetime.timedelta(seconds=1), datetime.datetime.now() - group.created)

    def test_date_created_unchanged_on_update(self):
        group = default_group()
        self.database.session.add(group)
        self.database.session.commit()
        date_created = group.created.replace()  # return a copy of datetime object
        group.name = "new-groupname"
        self.database.session.commit()
        self.assertEqual(date_created, group.created)

    def test_date_modified_default(self):
        group = default_group()
        self.database.session.add(group)
        self.database.session.commit()
        self.assertLess(datetime.timedelta(seconds=1), datetime.datetime.now() - group.modified)

    def test_date_modified_on_update(self):
        group = default_group()
        self.database.session.add(group)
        self.database.session.commit()
        date_modified = group.modified.replace()  # return a copy of datetime object
        group.name = "new-groupname"
        self.database.session.commit()
        self.assertNotEqual(date_modified, group.modified)
