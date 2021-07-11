#!/usr/bin/env python3

import logging
import os.path
from ssl import (
    SSLContext,
    CERT_REQUIRED
)
import tornado.ioloop
from tornado.options import (
    define,
    options
)
import tornado.web

from . import package_base
from storage_sqlite import Api
from http_request import (
    HttpRequestGroup,
    HttpRequestPassword,
    HttpRequestUser
)
from .auth_tokens import AuthorizationTokens
from .default_paths import DefaultPath
from error import InternalError

log = logging.getLogger(__name__)


define("db", default=DefaultPath.DATABASE, help="Path to database", type=str)
define("host", default="127.0.0.1", help="Listen address for server", type=str)
define("port", default=8025, help="Listen port for server", type=int)
define("verbose", help="Print database commands", type=bool)
define("generate-token", help="Generate a new authorization token for accessing passwords", type=bool)
define("token-db", default=DefaultPath.API_TOKENS, help="Path to authorization token database file", type=str)
define("cert_path", default=DefaultPath.TLS_CERT_PATH, group="tls", help="Prefix path for files", type=str)
define("cert_file", group="tls", help="Certificate file, example unix-accounts.lan.cert.pem", type=str)
define("key_file", group="tls", help="Key file, example unix-accounts.lan.key.pem", type=str)
define("ca_cert_file", group="tls", help="CA certificate chain file lan, example unix-accounts.lan.ca-chain.pem", type=str)


class ServerSSLContext(SSLContext):

    """ Ref: http://www.tornadoweb.org/en/stable/httputil.html?highlight=httpserverrequest#tornado.httputil.HTTPServerRequest.get_ssl_certificate """

    def __init__(self, cert: str, key: str, cacert: str, path = ""):
        super().__init__()
        self.load_cert_chain(
            os.path.join(path, cert),
            os.path.join(path, key)
        )
        if cacert:
            self.load_verify_locations(
                os.path.join(path, cacert))

    def set_verify_client_cert(self):
        self.verify_mode =  CERT_REQUIRED
        self.check_hostname = True


class Application:

    def __init__(self):
        self._api = Api(options.db, options.verbose)
        self._auth_tokens = AuthorizationTokens(options.token_db)

    def run(self):
        if options.generate_token:
            self._generate_token()
        else:
            self._run_server()

    def _generate_token(self):
        try:
            token = self._auth_tokens.generate_token()
            print("New access token added for accessing password api: \n\n    {token}\n".format(token=token))
        except OSError as err:
            print("Failed to generate token: {err}".format(err=err))

    def _run_server(self):
        server = tornado.web.Application([
            ("/api/group", HttpRequestGroup, dict(group_storage=self._api.groups)),
            ("/api/password", HttpRequestPassword, dict(password_storage=self._api.password, auth_tokens=self._try_load_auth_tokens())),
            ("/api/user", HttpRequestUser, dict(user_storage=self._api.users))
        ])

        if self._tls_args_provided():
            ssl_context = ServerSSLContext(
                options.cert_file,
                options.key_file,
                options.ca_cert_file,
                options.cert_path
            )
            ssl_context.set_verify_client_cert()
            server.listen(options.port, options.host, ssl_options=ssl_context)
        else:
            server.listen(options.port, options.host)
        log.info("Running server @ port {host}:{port}".format(
            host=options.host,
            port=options.port
        ))
        tornado.ioloop.IOLoop.current().start()

    def _try_load_auth_tokens(self):
        try:
            return self._auth_tokens.get_tokens()
        except OSError as err:
            log.warning("Failed to load authorization tokens: {}".format(err))
            return frozenset()

    @staticmethod
    def _tls_args_provided():
        return options.cert_file and options.key_file


def main():
    options.parse_command_line()
    try:
        application = Application()
        application.run()
    except InternalError as err:
        log.error("Failed to start server: {}".format(err))
    except KeyboardInterrupt:
        log.info("Goodbye!")


if __name__ == "__main__":
    main()
