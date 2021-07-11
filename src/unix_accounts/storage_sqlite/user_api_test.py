import unittest

from error import (
    AlreadyExist,
    DoesNotExist,
    NotPossible
)

from .schema import UnixAccountSchema
from .api import SqliteDatabase
from .user_api import UnixUserStorageSqlite
from .group_api import UnixGroupStorageSqlite


class Defaults:
    uid = 10
    username = "user"
    home_dir = "/home/user"
    gecos = "User Account Info"
    shell = "/bin/bash"
    group = "group"
    gid = 20


class UnixUserStorageTest(unittest.TestCase):

    def setUp(self):
        database = SqliteDatabase(
            UnixAccountSchema(),
            ":memory:",
            # verbose=True
        )
        self.users = UnixUserStorageSqlite(database)
        self.groups = UnixGroupStorageSqlite(database)

    def _default_userdata(self,
                          name=Defaults.username,
                          uid=Defaults.uid,
                          home_dir=Defaults.home_dir,
                          shell=Defaults.shell,
                          gecos=Defaults.gecos,
                          gid=None):
        return dict(name=name, uid=uid, gecos=gecos, gid=gid, home_dir=home_dir, shell=shell)

    def test_add_user(self):
        user_data = self._default_userdata()
        user = self.users.add(**user_data)
        self.assertEqual(Defaults.username, user.name)

    def test_add_user_with_existing_name(self):
        user_data = self._default_userdata()
        self.users.add(**user_data)
        another_user = self._default_userdata(uid=123)
        with self.assertRaises(AlreadyExist):
            self.users.add(**another_user)

    def test_add_user_with_existing_uid(self):
        user_data = self._default_userdata()
        self.users.add(**user_data)
        another_user = self._default_userdata(name="another-user")
        with self.assertRaises(AlreadyExist):
            self.users.add(**another_user)

    def test_add_user_with_no_gid(self):
        user_data = self._default_userdata()
        user = self.users.add(**user_data)
        # Create a group with same id + name as the user:
        self.assertEqual(Defaults.uid, user.group.id)
        self.assertEqual(Defaults.username, user.group.name)

    def test_add_user_with_occupied_uid_gid(self):
        self.groups.add(Defaults.group, Defaults.uid)
        user_data = self._default_userdata()
        user = self.users.add(**user_data)
        # create new group, even if uid==gid is not possible
        self.assertNotEqual(Defaults.uid, user.group.id)

    def test_add_user_with_gid(self):
        self.groups.add(Defaults.group, Defaults.gid)
        user_data = self._default_userdata(gid=Defaults.gid)
        user = self.users.add(**user_data)
        # use existing group:
        self.assertEqual(Defaults.gid, user.group.id)

    def test_add_user_with_invalid_gid(self):
        user_data = self._default_userdata(gid=Defaults.gid)
        with self.assertRaises(DoesNotExist):
            self.users.add(**user_data)

    def test_add_user_with_custom_uid(self):
        user_data = self._default_userdata()
        user = self.users.add(**user_data)
        self.assertEqual(user.uid, Defaults.uid)

    def test_add_user_without_uid_provided(self):
        user = self.users.add(name=Defaults.username)
        # don't throw

    def test_add_user_with_custom_home_dir(self):
        user_data = self._default_userdata()
        user = self.users.add(**user_data)
        self.assertEqual(user.home_dir, Defaults.home_dir)

    def test_add_user_with_custom_gecos(self):
        user_data = self._default_userdata()
        user = self.users.add(**user_data)
        self.assertEqual(user.gecos, Defaults.gecos)

    def test_add_user_with_custom_shell(self):
        user_data = self._default_userdata()
        user = self.users.add(**user_data)
        self.assertEqual(user.shell, Defaults.shell)

    def test_delete_user(self):
        user_data = self._default_userdata()
        self.users.add(**user_data)
        is_deleted = self.users.delete(Defaults.username)
        self.assertTrue(is_deleted)

    def test_delete_nonexisting_user(self):
        with self.assertRaises(DoesNotExist):
            self.users.delete(Defaults.username)

    def test_delete_users_group(self):
        user_data = self._default_userdata()
        user = self.users.add(**user_data)
        with self.assertRaises(NotPossible):
            self.groups.delete(user.name)

    def test_update_user_with_new_name(self):
        new_name = "new-name"
        self.users.add(**self._default_userdata())
        user = self.users.update_name(Defaults.username, new_name)
        self.assertEqual(new_name, user.name)

    def test_update_user_with_existing_new_name(self):
        existing_name = "existing-user"
        existing_uid = 123
        self.users.add(existing_name, existing_uid)
        self.users.add(**self._default_userdata())
        with self.assertRaises(AlreadyExist):
            self.users.update_name(Defaults.username, existing_name)

    def test_update_user_with_new_uid(self):
        self.users.add(**self._default_userdata())
        new_uid = 123
        user = self.users.update_id(Defaults.username, new_uid)
        self.assertEqual(new_uid, user.uid)

    def test_update_user_with_existing_new_uid(self):
        existing_uid = 123
        existing_name = "existing-user"
        self.users.add(existing_name, existing_uid)
        self.users.add(**self._default_userdata())
        with self.assertRaises(AlreadyExist):
            self.users.update_id(Defaults.username, existing_uid)

    def test_update_user_with_new_shell(self):
        self.users.add(**self._default_userdata())
        new_shell = "/bin/sh"
        user = self.users.update_shell(Defaults.username, new_shell)
        self.assertEqual(new_shell, user.shell)

    def test_update_user_with_new_gecos(self):
        self.users.add(**self._default_userdata())
        new_gecos = "New User Account info"
        user = self.users.update_gecos(Defaults.username, new_gecos)
        self.assertEqual(new_gecos, user.gecos)

    def test_update_user_with_new_home_dir(self):
        self.users.add(**self._default_userdata())
        new_home_dir = "/home/new-home"
        user = self.users.update_home_dir(Defaults.username, new_home_dir)
        self.assertEqual(new_home_dir, user.home_dir)

    def test_update_user_with_new_gid(self):
        self.users.add(**self._default_userdata())
        self.groups.add(Defaults.group, Defaults.gid)
        user = self.users.update_gid(Defaults.username, Defaults.gid)
        self.assertEqual(Defaults.gid, user.group.id)

    def test_update_user_with_non_existing_new_gid(self):
        self.users.add(**self._default_userdata())
        with self.assertRaises(DoesNotExist):
            self.users.update_gid(Defaults.username, Defaults.gid)

    def test_update_nonexisting_user(self):
        with self.assertRaises(DoesNotExist):
            self.users.update_id(Defaults.username, Defaults.uid)
        with self.assertRaises(DoesNotExist):
            self.users.update_name(Defaults.username, Defaults.username)
        with self.assertRaises(DoesNotExist):
            self.users.update_shell(Defaults.username, Defaults.shell)
        with self.assertRaises(DoesNotExist):
            self.users.update_home_dir(Defaults.username, Defaults.home_dir)
        with self.assertRaises(DoesNotExist):
            self.users.update_gid(Defaults.username, Defaults.gid)

    def test_get_nonexisting_user_by_name(self):
        with self.assertRaises(DoesNotExist):
            self.users.get_by_name(Defaults.username)

    def test_get_nonexisting_user_by_gid(self):
        with self.assertRaises(DoesNotExist):
            self.users.get_by_id(Defaults.uid)
