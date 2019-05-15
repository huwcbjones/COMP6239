import asyncio
import inspect
import os
import uuid

import tornado.web
from sqlalchemy.exc import OperationalError
from tornado.log import access_log

import backend.controllers
from backend import log
from backend.controller import Controller, WebSocketController
from backend.database import Database
from backend.models import User, OAuthClient, OAuthGrantType, OAuthResponseType
from backend.models.user import user_exists_by_email
from backend.utils import random_string


class App:

    def __init__(self, port, **kwargs):
        if __debug__:
            log.warning("DEBUG MODE IS ENABLED!")
            log.warning("Safeguards may be disabled.")
            log.warning("To disable this warning, run python with the -O flag")

        # errors = self._check_ports(port, kwargs.get("listen_port", 5998), kwargs.get("broadcast_port", 9850))
        # if len(errors) != 0:
        #     logging.fatal("Failed to bind to one or more ports")
        #     for k, e in errors.items():
        #         logging.fatal("Error binding: {}".format(k))
        #         logging.fatal(e.strerror)
        #     quit(1)

        try:
            db_host = os.environ.get("DATABASE_HOST", "localhost")
            db_port = os.environ.get("DATABASE_PORT", 5432)
            db_user = os.environ.get("DATABASE_USER", "postgres")
            db_password = os.environ.get("DATABASE_PASSWORD", "")
            db_db = os.environ.get("DATABASE_DB", "comp6239")

            self.db = self._init_database(db_host, int(db_port), db_user, db_password, db_db)
            self.db.recreate_db(if_not_exists=True)
            self._init_oauth_client()
        except OperationalError as e:
            log.fatal(e)
            quit(1)

        # try:
        #     self._init_elastic_search(es_host, es_port, kwargs.get("es_username"), kwargs.get("es_password"))
        # except ConnectionError as e:
        #     logging.fatal("Failed to connect to elastic search at {}:{}".format(es_host, es_port))
        #     logging.fatal(e.error)
        #     quit(1)

        # self._init_scoreboard_server(
        #     listen_port=kwargs.get("listen_port", 5998),
        #     listen_addr=kwargs.get("listen_addr"),
        #     broadcast_port=kwargs.get("broadcast_port", 9850),
        #     cluster_name=kwargs.get("cluster_name", "swimsuite"),
        #     bootstrap=kwargs.get("bootstrap", False)
        # )

        # Result.app = self

        app = self._make_app()
        try:
            app.listen(port, kwargs.get("listen_addr", ""))
        except OSError as e:
            log.fatal("Failed to listen on port {}".format(port))
            log.fatal(e.strerror)
            quit(1)

    def _load_route_class(self, obj, checked):
        routes = []
        # Loop through members of obj
        for name, obj in inspect.getmembers(obj):
            module = inspect.getmodule(obj)
            full_name = name
            if module:
                full_name = module.__name__ + "." + name
            if full_name in checked:
                continue
            checked.add(full_name)
            if name[0:2] == '__':
                continue

            if inspect.ismodule(obj):
                routes.extend(self._load_route_class(obj, checked))
                continue

            if not inspect.isclass(obj):
                continue

            if not issubclass(obj, (Controller, WebSocketController)):
                continue

            log.debug("Checking {}".format(name))
            if obj.route is not None:
                obj.app = self
                [routes.append((regex, obj)) for regex in obj.route]
                log.debug("Loaded {} routes for {}!".format(len(obj.route), name))

        return routes

    def _make_app(self):
        log.info("Loading controllers...")

        routes = self._load_route_class(backend.controllers, set())

        log.info("Loaded {} routes!".format(len(routes)))

        class DefaultController(Controller):

            def prepare(self):
                raise tornado.web.HTTPError(status_code=404)

        routes.append((r"[\w\W]*", DefaultController))
        return TornadoWebApp(routes)

    def _init_database(self, host: str, port: int, user: str, password: str, db: str = "comp6239"):

        return Database(
            host,
            port,
            user,
            password,
            database=db
        )

    def _init_oauth_client(self):
        service_user = None
        service_client = None
        service_password = random_string(20)
        if not user_exists_by_email("service@comp6239"):
            service_user = User(
                id=uuid.uuid4(),
                first_name="Service",
                last_name="Account",
                email="service@comp6239",
                password=service_password
            )
            service_client = OAuthClient(
                id=uuid.UUID("7834452b12ab480d9fc99f23b3546524"),
                client_secret=None,
                user_id=service_user.id,
                grant_type=OAuthGrantType.PASSWORD,
                response_type=OAuthResponseType.AUTHORIZATION_CODE,
                _scopes="*",
                _redirect_uris="http://localhost:8080/oauth/authorize"
            )
        admin_user = None
        admin_password = random_string(20)
        if not user_exists_by_email("admin@comp6239"):
            admin_user = User(
                id=uuid.uuid4(),
                first_name="Admin",
                last_name="Account",
                email="admin@comp6239",
                password=admin_password,
                role="ADMIN"
            )
        with self.db.session() as s:
            if service_user is not None:
                s.add(service_user)
                s.add(service_client)
            if admin_user is not None:
                s.add(admin_user)
            s.commit()
            if service_user is not None:
                log.info("Service Account: {} {}".format(service_user.email, service_password))
                log.info("OAuth Client ID: {}".format(service_client.client_id))
            if admin_user is not None:
                log.info("Admin Account: {} {}".format(admin_user.email, admin_password))

    def run(self):
        """
        Run the result server
        """
        log.info("Starting listen loop...")
        loop = asyncio.get_event_loop()
        loop.set_debug(True)
        try:
            loop.run_forever()
        except Exception:
            # Find all running tasks:
            pending = asyncio.Task.all_tasks()

            # Run loop until tasks done:
            loop.run_until_complete(asyncio.gather(*pending))
        finally:
            loop.stop()
            loop.close()


class TornadoWebApp(tornado.web.Application):

    def log_request(self, handler):
        # disable protected-access pylint: disable=W0212
        if handler.get_status() < 400:
            log_method = access_log.info
        elif handler.get_status() < 500:
            log_method = access_log.warning
        else:
            log_method = access_log.error
        request_time = 1000.0 * handler.request.request_time()
        log_method("{:d} {} {:.2f}ms".format(handler.get_status(), handler._request_summary(), request_time))
