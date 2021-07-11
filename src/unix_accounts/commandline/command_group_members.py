import argparse

from format import GroupsAsciiTable
from storage import UnixGroupMemberStorage

from .command import Command


class Mode:
    ADD, DELETE = "add", "del"


class CommandGroupMembers(Command):

    def __init__(self, parser: argparse.ArgumentParser, grp_member_storage: UnixGroupMemberStorage):
        self._register_commands(parser)
        self._parser = parser
        self._grp_member_storage = grp_member_storage

    @staticmethod
    def _register_commands(parser: argparse.ArgumentParser):
        subparsers = parser.add_subparsers(dest="group_member_command")
        cmd_add = subparsers.add_parser(Mode.ADD, help="Add user to group")
        cmd_add.add_argument("user", type=str, nargs=1, help="User name")
        cmd_add.add_argument("group", type=str, nargs=1, help="Group name")
        cmd_delete = subparsers.add_parser(Mode.DELETE, help="Remove user from group")
        cmd_delete.add_argument("user", type=str, nargs=1, help="User name")
        cmd_delete.add_argument("group", type=str, nargs=1, help="Group name")

    def exec(self, args: argparse.Namespace):
        cmd = CommandExec(args, self._grp_member_storage)
        success = cmd.exec()
        if not success:
            self._parser.print_help()


class CommandExec:

    def __init__(self, args: argparse.Namespace, grp_member_storage: UnixGroupMemberStorage):
        self._args = args
        self._grp_member_storage = grp_member_storage

    def exec(self) -> bool:
        if self._args.group_member_command == Mode.ADD:
            self._add()
        elif self._args.group_member_command == Mode.DELETE:
            self._delete()
        else:
            return False
        return True

    def _add(self):
        group = self._grp_member_storage.add_member(self._args.user[0], self._args.group[0])
        print(GroupsAsciiTable((group,)))

    def _delete(self):
        group = self._grp_member_storage.delete_member(self._args.user[0], self._args.group[0])
        print(GroupsAsciiTable((group,)))
