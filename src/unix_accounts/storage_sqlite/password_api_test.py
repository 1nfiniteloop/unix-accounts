import unittest

from error import DoesNotExist


from .schema import UnixAccountSchema
from .api import SqliteDatabase
from .user_api import UnixUserStorageSqlite
from .password_api import UnixPasswordStorageSqlite


class Defaults:
    user_name = "user"
    uid = 10000
    password = "secret"


class UnixPasswordStorageTest(unittest.TestCase):

    def setUp(self):
        database = SqliteDatabase(
            UnixAccountSchema(),
            ":memory:"
        )
        self.users = UnixUserStorageSqlite(database)
        self.password = UnixPasswordStorageSqlite(database)

    def test_set_password(self):
        self.users.add(Defaults.user_name)
        self.password.update(Defaults.user_name, Defaults.password)
        # don't throw

    def test_set_password_for_nonexisting_user(self):
        with self.assertRaises(DoesNotExist):
            self.password.update(Defaults.user_name, Defaults.password)

    def test_get_nonexisting_shadow_by_name(self):
        with self.assertRaises(DoesNotExist):
           self.password.get_by_name(Defaults.user_name)

    def test_get_shadow_by_name(self):
        self.users.add(Defaults.user_name)
        pwd = self.password.get_by_name(Defaults.user_name)
        # don't throw

    def test_get_all(self):
        self.users.add(Defaults.user_name)
        pwds = self.password.get_all()
        self.assertEqual(1, len(pwds))
