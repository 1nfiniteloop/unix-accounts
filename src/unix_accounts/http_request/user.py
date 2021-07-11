from typing import Dict
import tornado.web

from storage import UnixUserStorage
from format import (
    JsonFormatterUser,
)

from error import DoesNotExist


class Parameter(object):
    """ Valid parameters in http requests """
    USER_NAME = "name"
    USER_ID = "id"


class HttpRequestUser(tornado.web.RequestHandler):

    def initialize(self, user_storage: UnixUserStorage):
        self._user_storage = user_storage

    def get(self):
        try:
            self._try_get()
        except DoesNotExist as err:
            self.set_status(404, str(err))
        except ValueError as err:
            self.set_status(400, "user id is not a valid number")

    def _try_get(self):
        if Parameter.USER_ID in self.request.arguments:
            self.write(self._get_by_id(
                int(self.get_argument(Parameter.USER_ID))
            ))
        elif Parameter.USER_NAME in self.request.arguments:
            self.write(self._get_by_name(
                self.get_argument(Parameter.USER_NAME)
            ))
        elif not self.request.arguments:
            self.write(self._get_all())
        else:
            self.set_status(400)

    def _get_all(self) -> Dict:
        return {
            "all": list(JsonFormatterUser(user) for user in self._user_storage.get_all())
        }

    def _get_by_id(self, gid: int) -> Dict:
        return JsonFormatterUser(
            self._user_storage.get_by_id(gid)
        )

    def _get_by_name(self, name: str)-> Dict:
        return JsonFormatterUser(
            self._user_storage.get_by_name(name)
        )
