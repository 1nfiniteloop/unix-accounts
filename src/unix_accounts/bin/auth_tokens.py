import secrets
from typing import FrozenSet


class AuthorizationTokens:

    def __init__(self, filename: str):
        self._filename = filename

    def get_tokens(self) -> FrozenSet[str]:
        return self._read_tokens()

    def generate_token(self) -> str:
        token = secrets.token_urlsafe(32)
        self._write_token(token)
        return token

    def _write_token(self, token: str):
        with open(self._filename, "at") as file:
            file.write(token)
            file.write("\n")

    def _read_tokens(self) -> FrozenSet[str]:
        with open(self._filename, "r") as file:
            return frozenset(self._token_gen(file))

    def _token_gen(self, file):
        lines = file.read()
        for line in lines.split("\n"):
            if (line):
                yield line
