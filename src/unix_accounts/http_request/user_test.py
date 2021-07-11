from tornado.testing import AsyncHTTPTestCase
import tornado.web
import tornado.httputil
import tornado.escape
from unittest.mock import Mock

from error import DoesNotExist
from format import JsonAttributeUser
from user import UnixUser
from group import UnixGroup
from .user import (
    HttpRequestUser,
    Parameter,
)
from storage import UnixUserStorage


class Defaults:

    unix_group = UnixGroup(
        name="groupname",
        id_=10000,
        members=("first-user", "second-user")
    )
    unix_user = UnixUser(
        name="username",
        uid=10000,
        group=unix_group,
        gecos="some content",
        home_dir="/home/username",
        shell="bin/bash",
        group_membership=("first-group", "second-group")
    )


class Mocks:

    def __init__(self):
        self.storage = Mock(spec=UnixUserStorage)


class UsersTest(AsyncHTTPTestCase):
    API_ENDPOINT = "/api/users"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._mocks = Mocks()

    def setUp(self):
        super().setUp()
        self._mocks.storage.reset_mock()

    def get_app(self):
        return tornado.web.Application(
            handlers=[
                (self.API_ENDPOINT, HttpRequestUser, dict(user_storage=self._mocks.storage)),
            ])

    def test_get_all_users(self):
        self._mocks.storage.get_all.return_value = [
            Defaults.unix_user,
            Defaults.unix_user
        ]
        response = self.fetch(self.API_ENDPOINT, method="GET")
        decoded_response = tornado.escape.json_decode(response.body)
        self.assertEqual(200, response.code)
        self.assertIn("all", decoded_response)
        self.assertEqual(len(decoded_response["all"]), 2, "Expects to return two users")

    def test_get_all_users_when_non_existing(self):
        self._mocks.storage.get_all.return_value = []
        response = self.fetch(self.API_ENDPOINT, method="GET")
        decoded_response = tornado.escape.json_decode(response.body)
        self.assertEqual(200, response.code)
        self.assertIn("all", decoded_response)
        self.assertEqual(len(decoded_response["all"]), 0, "Expects to return empty list")

    def test_get_user_by_invalid_id(self):
        url = tornado.httputil.url_concat(self.API_ENDPOINT, {
            Parameter.USER_ID: "nan"
        })
        response = self.fetch(url, method="GET")
        self.assertEqual(400, response.code)

    def test_invalid_argument(self):
        url = tornado.httputil.url_concat(self.API_ENDPOINT, {
            "invalid-attribute": "nan"
        })
        response = self.fetch(url, method="GET")
        self.assertEqual(400, response.code)

    def test_get_user_by_id(self):
        self._mocks.storage.get_by_id.return_value = Defaults.unix_user
        url = tornado.httputil.url_concat(self.API_ENDPOINT, {
            Parameter.USER_ID: "10000"
        })
        response = self.fetch(url, method="GET")
        decoded_response = tornado.escape.json_decode(response.body)
        self.assertEqual(200, response.code)
        self._assert_attributes(decoded_response)

    def test_get_user_by_name(self):
        self._mocks.storage.get_by_name.return_value = Defaults.unix_user
        url = tornado.httputil.url_concat(self.API_ENDPOINT, {
            Parameter.USER_NAME: "user"
        })
        response = self.fetch(url, method="GET")
        decoded_response = tornado.escape.json_decode(response.body)
        self.assertEqual(200, response.code)
        self._assert_attributes(decoded_response)

    def _assert_attributes(self, decoded_response):
        self.assertEqual(Defaults.unix_user.name, decoded_response[JsonAttributeUser.name])
        self.assertEqual("x", decoded_response[JsonAttributeUser.password])
        self.assertEqual(Defaults.unix_user.uid, decoded_response[JsonAttributeUser.uid])
        self.assertEqual(Defaults.unix_user.group.id, decoded_response[JsonAttributeUser.gid])
        self.assertEqual(Defaults.unix_user.gecos, decoded_response[JsonAttributeUser.gecos])
        self.assertEqual(Defaults.unix_user.home_dir, decoded_response[JsonAttributeUser.dir])
        self.assertEqual(Defaults.unix_user.shell, decoded_response[JsonAttributeUser.shell])

    def test_get_non_existing_user_by_name(self):
        self._mocks.storage.get_by_name = Mock(side_effect=DoesNotExist())
        url = tornado.httputil.url_concat(self.API_ENDPOINT, {
            Parameter.USER_NAME: "user"
        })
        response = self.fetch(url, method="GET")
        self.assertEqual(404, response.code)

    def test_get_non_existing_user_by_uid(self):
        self._mocks.storage.get_by_id = Mock(side_effect=DoesNotExist())
        url = tornado.httputil.url_concat(self.API_ENDPOINT, {
            Parameter.USER_ID: "10000"
        })
        response = self.fetch(url, method="GET")
        self.assertEqual(404, response.code)
