from tornado.testing import AsyncHTTPTestCase
import tornado.web
import tornado.httputil
import tornado.escape
from unittest.mock import Mock

from error import DoesNotExist
from format import JsonAttributeGroup
from group import UnixGroup
from .group import (
    HttpRequestGroup,
    Parameter,
)
from storage import UnixGroupStorage


class Defaults:

    unix_group = UnixGroup(
        name="groupname",
        id_=10000,
        members=("first-user", "second-user")
    )


class Mocks:

    def __init__(self):
        self.storage = Mock(spec=UnixGroupStorage)


class GroupsTest(AsyncHTTPTestCase):
    API_ENDPOINT = "/api/groups"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._mocks = Mocks()

    def setUp(self):
        super().setUp()
        self._mocks.storage.reset_mock()

    def get_app(self):
        return tornado.web.Application(
            handlers=[
                (self.API_ENDPOINT, HttpRequestGroup, dict(group_storage=self._mocks.storage)),
            ])

    def test_get_all_groups(self):
        self._mocks.storage.get_all.return_value = [
            Defaults.unix_group,
            Defaults.unix_group
        ]
        response = self.fetch(self.API_ENDPOINT, method="GET")
        decoded_response = tornado.escape.json_decode(response.body)
        self.assertEqual(200, response.code)
        self.assertIn("all", decoded_response)
        self.assertEqual(len(decoded_response["all"]), 2, "Expects to return two groups")

    def test_get_all_groups_when_non_existing(self):
        self._mocks.storage.get_all.return_value = []
        response = self.fetch(self.API_ENDPOINT, method="GET")
        decoded_response = tornado.escape.json_decode(response.body)
        self.assertEqual(200, response.code)
        self.assertIn("all", decoded_response)
        self.assertEqual(len(decoded_response["all"]), 0, "Expects to return empty list")

    def test_get_group_by_invalid_id(self):
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

    def test_get_group_by_id(self):
        self._mocks.storage.get_by_id.return_value = Defaults.unix_group
        url = tornado.httputil.url_concat(self.API_ENDPOINT, {
            Parameter.USER_ID: "10000"
        })
        response = self.fetch(url, method="GET")
        decoded_response = tornado.escape.json_decode(response.body)
        self.assertEqual(200, response.code)
        self._assert_attributes(decoded_response)

    def test_get_group_by_name(self):
        self._mocks.storage.get_by_name.return_value = Defaults.unix_group
        url = tornado.httputil.url_concat(self.API_ENDPOINT, {
            Parameter.USER_NAME: "user"
        })
        response = self.fetch(url, method="GET")
        decoded_response = tornado.escape.json_decode(response.body)
        self.assertEqual(200, response.code)
        self._assert_attributes(decoded_response)

    def _assert_attributes(self, decoded_response):
        self.assertEqual(Defaults.unix_group.id, decoded_response[JsonAttributeGroup.gid])
        self.assertEqual(Defaults.unix_group.name, decoded_response[JsonAttributeGroup.name])
        self.assertEqual(Defaults.unix_group.id, decoded_response[JsonAttributeGroup.gid])
        self.assertSetEqual(set(Defaults.unix_group.members), set(decoded_response[JsonAttributeGroup.members]))

    def test_get_non_existing_group_by_name(self):
        self._mocks.storage.get_by_name = Mock(side_effect=DoesNotExist())
        url = tornado.httputil.url_concat(self.API_ENDPOINT, {
            Parameter.USER_NAME: "user"
        })
        response = self.fetch(url, method="GET")
        self.assertEqual(404, response.code)

    def test_get_non_existing_group_by_gid(self):
        self._mocks.storage.get_by_id = Mock(side_effect=DoesNotExist())
        url = tornado.httputil.url_concat(self.API_ENDPOINT, {
            Parameter.USER_ID: "10000"
        })
        response = self.fetch(url, method="GET")
        self.assertEqual(404, response.code)
