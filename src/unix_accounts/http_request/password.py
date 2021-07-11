from typing import Dict, FrozenSet
import tornado.web
import re

from storage import UnixPasswordStorage
from format import (
    JsonFormatterPassword,
)

from error import DoesNotExist


class Parameter(object):
    """ Valid parameters in http requests """
    USER_NAME = "name"


class HttpRequestPassword(tornado.web.RequestHandler):

    def initialize(self, password_storage: UnixPasswordStorage, auth_tokens: FrozenSet):
        self._password_storage = password_storage
        self._auth_tokens = auth_tokens

    def get(self):
        try:
            self._try_get()
        except DoesNotExist as err:
            self.set_status(404, str(err))
        except ValueError as err:
            self.set_status(400, "user id is not a valid number")

    def _try_get(self):
        bearer_token = self._get_bearer_token()
        if not bearer_token or bearer_token not in self._auth_tokens:
            self.set_status(401, "Bearer token unauthorized")
        elif Parameter.USER_NAME in self.request.arguments:
            self.write(self._get_by_name(
                self.get_argument(Parameter.USER_NAME)
            ))
        elif not self.request.arguments:
            self.write(self._get_all())
        else:
            self.set_status(400)

    def _get_bearer_token(self) -> str:
        token = ""
        if "authorization" in self.request.headers:
            value = self.request.headers["authorization"]
            match = re.match("[Bb]earer (.*)", value)
            if match:
                token = match.group(1)
        return token

    def _get_all(self) -> Dict:
        return {
            "all": list(JsonFormatterPassword(grp) for grp in self._password_storage.get_all())
        }

    def _get_by_name(self, name: str)-> Dict:
        return JsonFormatterPassword(
            self._password_storage.get_by_name(name)
        )
