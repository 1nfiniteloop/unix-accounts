import argparse
from getpass import getpass

from storage import UnixPasswordStorage
from .command import Command


class CommandPassword(Command):

    def __init__(self, parser: argparse.ArgumentParser, password_storage: UnixPasswordStorage):
        self._register_commands(parser)
        self._parser = parser
        self._password_storage = password_storage

    @staticmethod
    def _register_commands(parser: argparse.ArgumentParser):
        parser.add_argument("name", type=str, nargs=1, help="User name")

    def exec(self, args: argparse.Namespace):
        cmd = CommandExec(args, self._password_storage)
        cmd.exec()


class CommandExec:

    def __init__(self, args: argparse.Namespace, password_storage: UnixPasswordStorage):
        self._args = args
        self._password_storage = password_storage

    def exec(self):
        new_password = getpass(prompt="New password: ")
        self._password_storage.update(self._args.name[0], new_password)
