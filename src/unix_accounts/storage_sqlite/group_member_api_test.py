import unittest

from error import AlreadyExist, DoesNotExist

from .schema import UnixAccountSchema
from .api import SqliteDatabase
from .group_member_api import UnixGroupMemberStorageSqlite
from .user_api import UnixUserStorageSqlite
from .group_api import UnixGroupStorageSqlite


class Defaults:
    group = "group"
    user = "user"


class UnixGroupMemberStorageTest(unittest.TestCase):

    def setUp(self):
        database = SqliteDatabase(
            UnixAccountSchema(),
            ":memory:"
        )
        self.users = UnixUserStorageSqlite(database)
        self.groups = UnixGroupStorageSqlite(database)
        self.grp_member = UnixGroupMemberStorageSqlite(database)

    def _add_user_and_group(self):
        self.users.add(Defaults.user)
        self.groups.add(Defaults.group)

    def test_add_user_to_group(self):
        self._add_user_and_group()
        self.grp_member.add_member(Defaults.user, Defaults.group)
        grp = self.groups.get_by_name(Defaults.group)
        self.assertIn(Defaults.user, grp.members)

    def test_add_nonexisting_user_to_group(self):
        self._add_user_and_group()
        with self.assertRaises(DoesNotExist):
            self.grp_member.add_member("nonexisting-user", Defaults.group)

    def test_add_user_to_nonexisting_group(self):
        self._add_user_and_group()
        with self.assertRaises(DoesNotExist):
            self.grp_member.add_member(Defaults.user, "nonexisting-group")

    def test_add_already_existing_membership(self):
        self._add_user_and_group()
        self.grp_member.add_member(Defaults.user, Defaults.group)
        with self.assertRaises(AlreadyExist):
            self.grp_member.add_member(Defaults.user, Defaults.group)

    def test_delete_user_from_group(self):
        self._add_user_and_group()
        self.grp_member.add_member(Defaults.user, Defaults.group)
        self.grp_member.delete_member(Defaults.user, Defaults.group)
        grp = self.groups.get_by_name(Defaults.group)
        self.assertNotIn(Defaults.user, grp.members)

    def test_delete_nonexisting_user_from_group(self):
        self._add_user_and_group()
        with self.assertRaises(DoesNotExist):
            self.grp_member.delete_member("nonexisting-user", Defaults.group)

    def test_delete_user_to_nonexisting_group(self):
        self._add_user_and_group()
        with self.assertRaises(DoesNotExist):
            self.grp_member.delete_member(Defaults.user, "nonexisting-group")

    def test_delete_nonexisting_membership(self):
        self._add_user_and_group()
        with self.assertRaises(DoesNotExist):
            self.grp_member.delete_member(Defaults.user, Defaults.group)
