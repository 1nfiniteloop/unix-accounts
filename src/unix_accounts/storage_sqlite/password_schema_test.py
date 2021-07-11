import unittest
import datetime
import sqlalchemy.exc
import sqlalchemy.orm.exc

from .db_sqlite import SqliteDatabase
from .schema import (
    UnixAccountSchema,
    User,
    UserId,
    Password,
    Group,
    GroupId
)


class Defaults:
    user_name = "user"
    group_name = "grp"
    home_dir = "/home/user"
    hashed_password = "hashed-password"
    last_changed = "2000"


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


def default_password():
    return Password(
        name=Defaults.user_name,
        encrypted_password=Defaults.hashed_password,
        days_since_epoch_last_change=Defaults.last_changed
    )


class PasswordSchemaTest(unittest.TestCase):

    def setUp(self):
        self.database = SqliteDatabase(
            UnixAccountSchema(),
            ":memory:"
        )
        self.database.session.add(default_user())
        self.database.session.commit()

    def test_add_password(self):
        self.database.session.add(default_password())
        self.database.session.commit()

    def test_passwd_default(self):
        password = default_password()
        password.encrypted_password = None
        self.database.session.add(password)
        self.database.session.commit()
        self.assertEqual(Password.DEFAULT_PASSWD, password.encrypted_password)

    def test_lastchange_default(self):
        password = default_password()
        password.days_since_epoch_last_change = None
        self.database.session.add(password)
        self.database.session.commit()
        days_since_epoch = datetime.datetime.now() - datetime.datetime(1970, 1, 1)
        self.assertEqual(days_since_epoch.days, password.days_since_epoch_last_change)

    def test_min_default(self):
        password = default_password()
        self.database.session.add(password)
        self.database.session.commit()
        self.assertEqual(Password.DEFAULT_MIN, password.days_min)

    def test_max_default(self):
        password = default_password()
        self.database.session.add(password)
        self.database.session.commit()
        self.assertEqual(Password.DEFAULT_MAX, password.days_max)

    def test_warn_default(self):
        password = default_password()
        self.database.session.add(password)
        self.database.session.commit()
        self.assertEqual(Password.DEFAULT_WARN, password.days_warn)

    def test_inact_default(self):
        password = default_password()
        self.database.session.add(password)
        self.database.session.commit()
        self.assertIsNone(password.days_inactive)

    def test_expire_default(self):
        password = default_password()
        self.database.session.add(password)
        self.database.session.commit()
        self.assertIsNone(password.days_since_epoch_expires)


class UserPasswordRelationTest(unittest.TestCase):

    def setUp(self):
        self.database = SqliteDatabase(
            UnixAccountSchema(),
            ":memory:"
        )

    def test_add_password_on_nonexistent_user(self):
        password = default_password()
        password.name = "non-existing"
        self.database.session.add(password)
        with self.assertRaisesRegex(sqlalchemy.exc.IntegrityError, "FOREIGN KEY constraint failed"):
            self.database.session.commit()

    def test_cascaded_delete(self):
        self.database.session.add_all((
            default_password(),
            default_user()
        ))
        self.database.session.commit()
        self.database.session.query(User).delete()
        with self.assertRaises(sqlalchemy.orm.exc.NoResultFound):
            self.database.session.query(Password).filter(User.name == Defaults.user_name).one()

    def test_foreign_key_constraint(self):
        self.database.session.add_all((
            # no user added
            default_password(),
        ))
        with self.assertRaises(sqlalchemy.exc.IntegrityError):
            self.database.session.commit()
