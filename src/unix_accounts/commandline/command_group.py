import argparse

from format import GroupsAsciiTable
from storage import UnixGroupStorage
from error import InternalError

from .command import Command


class Mode:
    ADD, GET, UPDATE, DELETE = "add", "get", "update", "del"


class CommandGroup(Command):

    def __init__(self, parser: argparse.ArgumentParser, group_storage: UnixGroupStorage):
        self._register_commands(parser)
        self._parser = parser
        self._group_storage = group_storage

    @staticmethod
    def _register_commands(parser: argparse.ArgumentParser):
        subparsers = parser.add_subparsers(dest="groups_command")
        cmd_add = subparsers.add_parser(Mode.ADD)
        cmd_add.add_argument("name", type=str, nargs=1, help="Group name")
        cmd_add.add_argument("--gid", type=int, help="Group id")
        cmd_get = subparsers.add_parser(Mode.GET)
        cmd_get.add_argument("--gid", type=int)
        cmd_get.add_argument("name", type=str, nargs="?")
        cmd_delete = subparsers.add_parser(Mode.DELETE)
        cmd_delete.add_argument("name", type=str, help="Group name")
        cmd_update = subparsers.add_parser(Mode.UPDATE)
        cmd_update.add_argument("name", type=str, help="Group name")
        grp = cmd_update.add_mutually_exclusive_group()
        grp.add_argument("--new-gid", type=int)
        grp.add_argument("--new-name", type=str)

    def exec(self, args: argparse.Namespace):
        cmd = CommandExec(args, self._group_storage)
        success = cmd.exec()
        if not success:
            self._parser.print_help()


class CommandExec:

    def __init__(self, args: argparse.Namespace, group_storage: UnixGroupStorage):
        self._args = args
        self._group_storage = group_storage

    def exec(self) -> bool:
        if self._args.groups_command == Mode.ADD:
            self._add()
        elif self._args.groups_command == Mode.GET:
            self._get()
        elif self._args.groups_command == Mode.DELETE:
            self._delete()
        elif self._args.groups_command == Mode.UPDATE:
            self._update()
        else:
            return False
        return True

    def _add(self):
        group = self._group_storage.add(self._args.name[0], self._args.gid)
        print(GroupsAsciiTable((group,)))

    def _get(self):
        if self._args.gid:
            groups = (self._group_storage.get_by_id(self._args.gid),)
        elif self._args.name:
            groups = (self._group_storage.get_by_name(self._args.name),)
        else:
            groups = self._group_storage.get_all()
        print(GroupsAsciiTable(groups))

    def _delete(self):
        self._group_storage.delete(self._args.name)

    def _update(self):
        if self._args.new_gid:
            groups = (self._group_storage.update_id(self._args.name, self._args.new_gid),)
        elif self._args.new_name:
            groups = (self._group_storage.update_name(self._args.name, self._args.new_name),)
        else:
            raise InternalError("Cmdline: this shall never happen")
        print(GroupsAsciiTable(groups))
