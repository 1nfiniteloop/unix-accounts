import unittest

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


class UserGroupMembershipTest(unittest.TestCase):

    def setUp(self):
        self.database = SqliteDatabase(
            UnixAccountSchema(),
            ":memory:"
        )

    def test_add_user_to_group(self):
        user = default_user()
        group = default_group()
        group.name = "another-group"
        user.group_membership.append(group)
        self.database.session.add(user)
        self.database.session.commit()
        self.assertIn(group, user.group_membership)
        self.assertIn(user, group.user_membership)

    def test_remove_group_from_user(self):
        user = default_user()
        group = default_group()
        group.name = "another-group"
        user.group_membership.append(group)
        self.database.session.add(user)
        self.database.session.commit()
        user.group_membership.remove(group)
        self.database.session.commit()
        self.assertNotIn(group, user.group_membership)
        self.assertNotIn(user, group.user_membership)

    def test_user_backpopulates_groups(self):
        user = default_user()
        group = default_group()
        group.name = "another-group"
        group.user_membership.append(user)
        self.database.session.add_all((user, group))
        self.database.session.commit()
        self.assertIn(group, user.group_membership)

    def test_group_backpopulates_users(self):
        user = default_user()
        group = default_group()
        group.name = "another-group"
        user.group_membership.append(group)
        self.database.session.add_all((group, user))
        self.database.session.commit()
        self.assertIn(user, group.user_membership)
