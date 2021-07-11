import unittest

from error import AlreadyExist, DoesNotExist

from .schema import UnixAccountSchema
from .api import SqliteDatabase
from .user_api import UnixUserStorageSqlite
from .group_api import UnixGroupStorageSqlite


class Defaults:
    group = "group"
    gid = 10000


class UnixGroupStorageTest(unittest.TestCase):

    def setUp(self):
        database = SqliteDatabase(
            UnixAccountSchema(),
            ":memory:"
        )
        self.users = UnixUserStorageSqlite(database)
        self.groups = UnixGroupStorageSqlite(database)

    def test_add_group(self):
        group = self.groups.add(Defaults.group)
        self.assertEqual(Defaults.group, group.name)

    def test_add_group_with_existing_name(self):
        self.groups.add(Defaults.group)
        with self.assertRaises(AlreadyExist):
            self.groups.add(Defaults.group)

    def test_add_group_with_existing_id(self):
        self.groups.add(Defaults.group, Defaults.gid)
        with self.assertRaises(AlreadyExist):
            self.groups.add(Defaults.group, Defaults.gid)

    def test_delete_group(self):
        self.groups.add(Defaults.group, Defaults.gid)
        self.groups.delete(Defaults.group)
        # Don't throw

    def test_delete_nonexisting_group(self):
        with self.assertRaises(DoesNotExist):
            self.groups.delete(Defaults.group)

    def test_update_group_with_new_name(self):
        new_name = "new-name"
        self.groups.add(Defaults.group, Defaults.gid)
        group = self.groups.update_name(Defaults.group, new_name)
        self.assertEqual(new_name, group.name)

    def test_update_group_with_new_id(self):
        self.groups.add(Defaults.group, Defaults.gid)
        new_gid = 123
        group = self.groups.update_id(Defaults.group, new_gid)
        self.assertEqual(new_gid, group.id)

    def test_update_group_with_existing_new_name(self):
        existing_name = "existing-group"
        existing_gid = 123
        self.groups.add(existing_name, existing_gid)
        self.groups.add(Defaults.group, Defaults.gid)
        with self.assertRaises(AlreadyExist):
            self.groups.update_name(Defaults.group, existing_name)

    def test_update_group_with_existing_new_id(self):
        existing_gid = 123
        existing_name = "existing-group"
        self.groups.add(existing_name, existing_gid)
        self.groups.add(Defaults.group, Defaults.gid)
        with self.assertRaises(AlreadyExist):
            self.groups.update_id(Defaults.group, existing_gid)

    def test_update_nonexisting_group(self):
        with self.assertRaises(DoesNotExist):
            self.groups.update_id(Defaults.group, Defaults.gid)
        with self.assertRaises(DoesNotExist):
            self.groups.update_name(Defaults.group, Defaults.group)

    def test_get_nonexisting_group_by_name(self):
        with self.assertRaises(DoesNotExist):
           self.groups.get_by_name(Defaults.group)

    def test_get_nonexisting_group_by_gid(self):
        with self.assertRaises(DoesNotExist):
           self.groups.get_by_id(Defaults.gid)
