from typing import Dict
from tornado.testing import AsyncHTTPTestCase
import tornado.web
import tornado.httputil
import tornado.escape
from unittest.mock import Mock

from error import DoesNotExist
from format import JsonAttributePassword
from password import UnixPassword
from .password import (
    HttpRequestPassword,
    Parameter,
)
from storage import UnixPasswordStorage


class Defaults:

    auth_token = "MOmlarDvdZtXF8R81OqGrDfbWE66ljNwXmuZUj4X1dQ"
    unix_password = UnixPassword(
        name="passwordname",
        encrypted_password="asd",
        days_since_epoch_last_change=2000,
        days_min=100,
        days_max=200,
        days_warn=150,
        days_inactive=100,
        days_since_epoch_expires=3000
    )


def default_headers() -> Dict[str, str]:
    return {
        "authorization": "Bearer {}".format(Defaults.auth_token)
    }


class Mocks:

    def __init__(self):
        self.storage = Mock(spec=UnixPasswordStorage)


class PasswordsTest(AsyncHTTPTestCase):
    API_ENDPOINT = "/api/passwords"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._mocks = Mocks()

    def setUp(self):
        super().setUp()
        self._mocks.storage.reset_mock()

    def get_app(self):
        return tornado.web.Application(
            handlers=[
                (self.API_ENDPOINT, HttpRequestPassword, dict(password_storage=self._mocks.storage, auth_tokens={
                    Defaults.auth_token})),
            ])

    def test_get_all_passwords(self):
        self._mocks.storage.get_all.return_value = [
            Defaults.unix_password,
            Defaults.unix_password
        ]
        response = self.fetch(self.API_ENDPOINT, headers=default_headers())
        decoded_response = tornado.escape.json_decode(response.body)
        self.assertEqual(200, response.code)
        self.assertIn("all", decoded_response)
        self.assertEqual(len(decoded_response["all"]), 2, "Expects to return two passwords")

    def test_get_all_passwords_when_non_existing(self):
        self._mocks.storage.get_all.return_value = []
        response = self.fetch(self.API_ENDPOINT, headers=default_headers())
        decoded_response = tornado.escape.json_decode(response.body)
        self.assertEqual(200, response.code)
        self.assertIn("all", decoded_response)
        self.assertEqual(len(decoded_response["all"]), 0, "Expects to return empty list")

    def test_invalid_argument(self):
        url = tornado.httputil.url_concat(self.API_ENDPOINT, {
            "invalid-attribute": "nan"
        })
        response = self.fetch(url, headers=default_headers())
        self.assertEqual(400, response.code)

    def test_get_password_by_name(self):
        self._mocks.storage.get_by_name.return_value = Defaults.unix_password
        url = tornado.httputil.url_concat(self.API_ENDPOINT, {
            Parameter.USER_NAME: "user"
        })
        response = self.fetch(url, headers=default_headers())
        decoded_response = tornado.escape.json_decode(response.body)
        self.assertEqual(200, response.code)
        self._assert_attributes(decoded_response)

    def _assert_attributes(self, decoded_response):
        self.assertEqual(Defaults.unix_password.name, decoded_response[JsonAttributePassword.name])
        self.assertEqual(Defaults.unix_password.encrypted_password, decoded_response[JsonAttributePassword.password])
        self.assertEqual(Defaults.unix_password._days_since_epoch_last_change, decoded_response[JsonAttributePassword.last_change])
        self.assertEqual(Defaults.unix_password.days_min, decoded_response[JsonAttributePassword.days_min])
        self.assertEqual(Defaults.unix_password.days_max, decoded_response[JsonAttributePassword.days_max])
        self.assertEqual(Defaults.unix_password.days_warn, decoded_response[JsonAttributePassword.days_warn])
        self.assertEqual(Defaults.unix_password.days_inactive, decoded_response[JsonAttributePassword.days_inactive])
        self.assertEqual(Defaults.unix_password.days_since_epoch_expires, decoded_response[JsonAttributePassword.expire])

    def test_get_non_existing_password_by_name(self):
        self._mocks.storage.get_by_name = Mock(side_effect=DoesNotExist())
        url = tornado.httputil.url_concat(self.API_ENDPOINT, {
            Parameter.USER_NAME: "user"
        })
        response = self.fetch(url, headers=default_headers())
        self.assertEqual(404, response.code)

    def test_no_authorization_header(self):
        response = self.fetch(self.API_ENDPOINT)
        self.assertEqual(401, response.code)

    def test_invalid_authorization_header(self):
        response = self.fetch(self.API_ENDPOINT, headers={"authorization": "foo"})
        self.assertEqual(401, response.code)

    def test_unautorized_bearer_token(self):
        response = self.fetch(self.API_ENDPOINT, headers={"Authorization": "Bearer foo"})
        self.assertEqual(401, response.code)

    def test_authorized_bearer_token(self):
        self._mocks.storage.get_all.return_value = []
        response = self.fetch(self.API_ENDPOINT, headers=default_headers())
        self.assertEqual(200, response.code)
