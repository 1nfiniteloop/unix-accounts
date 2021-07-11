#!/usr/bin/env python3

from typing import List
import argparse
import readline # import is enough to enable readline for "input()" prompt
import shlex

from . import package_base
from storage_sqlite import Api
from commandline import (
    CommandUnixAccount
)
from error import (
    UnixAccountError,
    InternalError
)
from .default_paths import DefaultPath


readline.parse_and_bind('tab: complete')


class ArgumentParseError(Exception):
    pass


class UnixAccountArgumentParser(argparse.ArgumentParser):

    def exit(self,status=0, message=None):
        raise ArgumentParseError(message)


class Application:
    PROMPT = "unix-accounts# "

    def __init__(self):
        app_parser = self._build_application_parser()
        # TODO parse below can throw (on "--help", only), where to handle that??
        args, remaining_cmdline_args = app_parser.parse_known_args()
        self._api = Api(args.db, args.verbose)
        self._remaining_cmdline_args = remaining_cmdline_args

    # TODO: this will consume the --help and not propagate to subparsers..
    def _build_application_parser(self) -> argparse.ArgumentParser:
        parser = self._get_parser()
        parser.add_argument("--db", type=str, default=DefaultPath.DATABASE, help="Path to database")
        parser.add_argument("--verbose", action="store_true", help="Print database commands")
        return parser

    @staticmethod
    def _get_parser() -> argparse.ArgumentParser:
        return UnixAccountArgumentParser(description="unix account shell")

    def run(self):
        if self._remaining_cmdline_args:
            self._run_once(self._remaining_cmdline_args)
        else:
            self._run_interactive()

    def _run_interactive(self):
        try:
            self._try_run_interactive()
        except EOFError:
            print("")
        print("Bye!")

    def _try_run_interactive(self):
        while True:
            try:
                cmd = input(self.PROMPT)
            except KeyboardInterrupt:
                print("")
                continue
            if cmd in ("exit", "quit"):
                break
            elif not cmd:
                pass
            else:
                # preserve quoted content when split string:
                self._run_once(shlex.split(cmd))

    def _run_once(self, cmdline_args: List[str]):
        try:
            self._try_run_once(cmdline_args)
        except ArgumentParseError as err:
            print("\n{}".format(err))
        except UnixAccountError as err:
            print("ERROR: {error}".format(error=err))

    def _try_run_once(self, cmdline_args: List[str]):
        parser = self._get_parser()
        cmd = CommandUnixAccount(parser, self._api)
        args = parser.parse_args(cmdline_args)
        cmd.exec(args)


def main():
    try:
        app = Application()
        app.run()
    except ArgumentParseError as err:
        exit(1)
    except InternalError as err:
        print(err)
        exit(1)


if __name__ == "__main__":
    main()
