import argparse

from storage_sqlite import Api
from .command import Command
from .command_group import CommandGroup
from .command_user import CommandUsers
from .command_group_members import CommandGroupMembers
from .command_password import CommandPassword


class Mode:
    GROUP = "group"
    USER = "user"
    GROUP_MEMBER = "group-member"
    PASSWORD = "password"


class CommandUnixAccount(Command):

    def __init__(self, parser: argparse.ArgumentParser, api: Api):
        self._parser = parser
        self._api = api
        self._subcommands = self._register_commands(parser)

    def _register_commands(self, parser: argparse.ArgumentParser):
        subparsers = parser.add_subparsers(dest="command")
        return {
            Mode.GROUP: CommandGroup(subparsers.add_parser(Mode.GROUP, help="Group commands"), self._api.groups),
            Mode.USER: CommandUsers(subparsers.add_parser(Mode.USER, help="User commands"), self._api.users),
            Mode.GROUP_MEMBER: CommandGroupMembers(subparsers.add_parser(Mode.GROUP_MEMBER, help="Group membership commands"), self._api.group_members),
            Mode.PASSWORD: CommandPassword(subparsers.add_parser(Mode.PASSWORD, help="Group membership commands"), self._api.password)
        }

    def exec(self, args: argparse.Namespace):
        if args.command in self._subcommands:
            cmd = self._subcommands[args.command]
            cmd.exec(args)
        else:
            self._parser.print_help()
