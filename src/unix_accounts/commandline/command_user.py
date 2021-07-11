import argparse

from format import UsersAsciiTable
from storage import UnixUserStorage
from error import InternalError

from .command import Command


class Mode:
    ADD, GET, UPDATE, DELETE = "add", "get", "update", "del"


class CommandUsers(Command):

    def __init__(self, parser: argparse.ArgumentParser, user_storage: UnixUserStorage):
        self._register_commands(parser)
        self._parser = parser
        self._user_storage = user_storage

    @staticmethod
    def _register_commands(parser: argparse.ArgumentParser):
        subparsers = parser.add_subparsers(dest="users_command")
        cmd_add = subparsers.add_parser(Mode.ADD)
        cmd_add.add_argument("name", type=str, nargs=1, help="User name")
        cmd_add.add_argument("--uid", type=int, help="User id")
        cmd_add.add_argument("--gecos", type=str, help="User account info")
        cmd_add.add_argument("--home-dir", type=str, help="Users home")
        cmd_add.add_argument("--shell", type=str, help="Users login shell")
        cmd_get = subparsers.add_parser(Mode.GET)
        cmd_get.add_argument("name", type=str, nargs="?")
        cmd_get.add_argument("--uid", type=int)
        cmd_delete = subparsers.add_parser(Mode.DELETE)
        cmd_delete.add_argument("name", type=str, help="User name")
        cmd_update = subparsers.add_parser(Mode.UPDATE)
        cmd_update.add_argument("name", type=str, help="User name")
        grp = cmd_update.add_mutually_exclusive_group()
        grp.add_argument("--new-uid", type=int)
        grp.add_argument("--new-gid", type=int)
        grp.add_argument("--new-name", type=str)
        grp.add_argument("--new-gecos", type=str)
        grp.add_argument("--new-home-dir", type=str)
        grp.add_argument("--new-shell", type=str)

    def exec(self, args: argparse.Namespace):
        cmd = CommandExec(args, self._user_storage)
        success = cmd.exec()
        if not success:
            self._parser.print_help()


class CommandExec:

    def __init__(self, args: argparse.Namespace, user_storage: UnixUserStorage):
        self._args = args
        self._user_storage = user_storage

    def exec(self) -> bool:
        mode = self._args.users_command
        if mode == Mode.ADD:
            self._add()
        elif mode == Mode.GET:
            self._get()
        elif mode == Mode.DELETE:
            self._delete()
        elif mode == Mode.UPDATE:
            self._update()
        else:
            return False
        return True

    def _add(self):
        new_user = self._user_storage.add(
            name=self._args.name[0],
            uid=self._args.uid,
            gecos=self._args.gecos,
            home_dir=self._args.home_dir,
            shell=self._args.shell
        )
        print(UsersAsciiTable((new_user,)))

    def _get(self):
        if self._args.uid:
            users = (self._user_storage.get_by_id(self._args.uid),)
        elif self._args.name:
            users = (self._user_storage.get_by_name(self._args.name),)
        else:
            users = self._user_storage.get_all()
        print(UsersAsciiTable(users))

    def _delete(self):
        self._user_storage.delete(self._args.name)

    def _update(self):
        if self._args.new_uid:
            users = (self._user_storage.update_id(self._args.name, self._args.new_uid),)
        elif self._args.new_gid:
            users = (self._user_storage.update_gid(self._args.name, self._args.new_gid),)
        elif self._args.new_name:
            users = (self._user_storage.update_name(self._args.name, self._args.new_name),)
        elif self._args.new_gecos:
            users = (self._user_storage.update_gecos(self._args.name, self._args.new_gecos),)
        elif self._args.new_home_dir:
            users = (self._user_storage.update_home_dir(self._args.name, self._args.new_home_dir),)
        elif self._args.new_shell:
            users = (self._user_storage.update_shell(self._args.name, self._args.new_shell),)
        else:
            raise InternalError("Cmdline: this shall never happen")
        print(UsersAsciiTable(users))
