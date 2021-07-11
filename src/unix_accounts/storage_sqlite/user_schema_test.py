import unittest
import datetime
import sqlalchemy.exc
import sqlalchemy.orm.exc

from .db_sqlite import SqliteDatabase
from .schema import (
    UnixAccountSchema,
    Group,
    GroupId,
    User,
    UserId
)


class Defaults:
    user_name = "user"
    user_id = 10000
    group_name = "group"
    home_dir = "/home/user"
    gecos = "User Account Info"
    shell = "/bin/bash"


def default_group():
    return Group(
        name=Defaults.group_name,
        group_id=GroupId()
    )


def default_user():
    user = User(
        name=Defaults.user_name,
        home_dir=Defaults.home_dir,
        user_id=UserId()
    )
    user.group = default_group()
    return user


class UserSchemaTest(unittest.TestCase):

    def setUp(self):
        self.database = SqliteDatabase(
            UnixAccountSchema(),
            ":memory:",
            # verbose=True
        )

    def test_add_user(self):
        user = default_user()
        self.database.session.add(user)
        self.database.session.commit()
        fetched_user = self.database.session.query(User).one()
        self.assertEqual(user, fetched_user)

    # delete UserId and cascade delete User, from database layer
    def test_db_remove_user_and_its_user_id(self):
        user = default_user()
        user.user_id.id = Defaults.user_id
        self.database.session.add(user)
        self.database.session.commit()
        user = self.database.session.query(User).filter(User.name == Defaults.user_name).one()
        self.database.session.query(UserId).filter(UserId.id == user.id).delete()
        with self.assertRaises(sqlalchemy.orm.exc.NoResultFound):
            _ = self.database.session.query(UserId).filter(UserId.id == 10000).one()

    # delete User and UserId, from object relation mappers
    def test_orm_remove_user_and_its_user_id(self):
        user = default_user()
        user.user_id.id = Defaults.user_id
        self.database.session.add(user)
        self.database.session.commit()
        user = self.database.session.query(User).filter(User.name == Defaults.user_name).one()
        self.database.session.delete(user)
        with self.assertRaises(sqlalchemy.orm.exc.NoResultFound):
            _ = self.database.session.query(UserId).filter(UserId.id == 10000).one()

    def test_name_required(self):
        user = default_user()
        user.name = None
        self.database.session.add(user)
        with self.assertRaisesRegex(sqlalchemy.exc.IntegrityError, "user.name"):
            self.database.session.commit()

    def test_home_dir_required(self):
        user = default_user()
        user.home_dir = None
        self.database.session.add(user)
        with self.assertRaisesRegex(sqlalchemy.exc.IntegrityError, "user.home_dir"):
            self.database.session.commit()

    def test_shell_default(self):
        user = default_user()
        user.shell = None
        self.database.session.add(user)
        self.database.session.commit()
        self.assertEqual(User.DEFAULT_SHELL, user.shell)

    def test_name_must_be_unique(self):
        first = default_user()
        second = default_user()
        second.group.name = "second-group"
        self.database.session.add_all((first, second))
        with self.assertRaisesRegex(sqlalchemy.exc.IntegrityError, "user.name"):
            self.database.session.commit()

    def test_uid_auto_increment(self):
        first = default_user()
        first.group.id = 10000
        second = default_user()
        second.name = "second-user"
        second.group.name = "second-group"
        self.database.session.add_all((first, second))
        self.database.session.commit()
        self.assertEqual(first.id + 1, second.id)

    def test_gid_required(self):
        user = default_user()
        user.group = None
        self.database.session.add(user)
        with self.assertRaisesRegex(sqlalchemy.exc.IntegrityError, "user.gid"):
            self.database.session.commit()

    def test_date_created_default(self):
        user = default_user()
        self.database.session.add(user)
        self.database.session.commit()
        self.assertLess(datetime.timedelta(seconds=1), datetime.datetime.now() - user.created)

    def test_date_created_unchanged_on_update(self):
        user = default_user()
        self.database.session.add(user)
        self.database.session.commit()
        date_created = user.created.replace()  # returns a copy of datetime object
        user.name = "new-username"
        self.database.session.commit()
        self.assertEqual(date_created, user.created)

    def test_date_modified_default(self):
        user = default_user()
        self.database.session.add(user)
        self.database.session.commit()
        self.assertLess(datetime.timedelta(seconds=1), datetime.datetime.now() - user.modified)

    def test_date_modified_on_update(self):
        user = default_user()
        self.database.session.add(user)
        self.database.session.commit()
        date_modified = user.modified.replace()  # return a copy of datetime object
        user.name = "new-username"
        self.database.session.commit()
        self.assertNotEqual(date_modified, user.modified)


# a user have a default group assigned
class UsersGroupMembershipTest(unittest.TestCase):

    def setUp(self):
        self.database = SqliteDatabase(
            UnixAccountSchema(),
            ":memory:",
        )

    def test_add_group_to_user(self):
        user = default_user()
        grp = default_group()
        user.group = grp
        self.database.session.add(user)
        self.database.session.commit()
        self.assertEqual(grp.id, user.gid)

    def test_delete_group_from_user(self):
        user = default_user()
        self.database.session.add(user)
        self.database.session.commit()
        self.database.session.delete(user.group)
        with self.assertRaises(sqlalchemy.exc.IntegrityError):
            self.database.session.commit()
