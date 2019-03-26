import asyncio
import inspect
import logging
import uuid

import tornado.web
from sqlalchemy.exc import OperationalError

import backend.controllers
from backend.controller import Controller, WebSocketController
from backend.database import Database
from backend.models import User, OAuthClient, OAuthGrantType, OAuthResponseType
from backend.utils import random_string

logger = logging.getLogger(__name__)


class App:

    def __init__(self, port, **kwargs):
        if __debug__:
            logger.warning("DEBUG MODE IS ENABLED!")
            logger.warning("Safeguards may be disabled.")
            logger.warning("To disable this warning, run python with the -O flag")

        # errors = self._check_ports(port, kwargs.get("listen_port", 5998), kwargs.get("broadcast_port", 9850))
        # if len(errors) != 0:
        #     logging.fatal("Failed to bind to one or more ports")
        #     for k, e in errors.items():
        #         logging.fatal("Error binding: {}".format(k))
        #         logging.fatal(e.strerror)
        #     quit(1)

        try:
            self.db = self._init_database("localhost", 5432, "postgres", "")
            self.db.recreate_db()
            self._init_oauth_client()
        except OperationalError as e:
            logging.fatal(e)
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
            logger.fatal("Failed to listen on port {}".format(port))
            logger.fatal(e.strerror)
            quit(1)

    def _load_route_class(self, obj, checked):
        routes = []
        # Loop through members of obj
        for name, obj in inspect.getmembers(obj):
            if name in checked:
                continue
            checked.add(name)
            if name[0:2] == '__':
                continue

            if inspect.ismodule(obj):
                routes.extend(self._load_route_class(obj, checked))
                continue

            if not inspect.isclass(obj):
                continue

            if not issubclass(obj, (Controller, WebSocketController)):
                continue

            logger.debug("Checking {}".format(name))
            if obj.route is not None:
                obj.app = self
                [routes.append((regex, obj)) for regex in obj.route]
                logger.debug("Loaded {} routes for {}!".format(len(obj.route), name))

        return routes

    def _make_app(self):
        logger.info("Loading controllers...")

        routes = self._load_route_class(backend.controllers, set())

        logger.info("Loaded {} routes!".format(len(routes)))

        class DefaultController(Controller):

            def prepare(self):
                raise tornado.web.HTTPError(status_code=404)

        routes.append((r"[\w\W]*", DefaultController))
        return tornado.web.Application(routes)

    def _init_database(self, host: str, port: int, user: str, password: str):

        return Database(
            host,
            port,
            user,
            password
        )

    def _init_oauth_client(self):
        service_password = random_string(20)
        admin_password = random_string(20)
        service_user = User(
            id=uuid.uuid4(),
            first_name="Service",
            last_name="Account",
            email="service@comp6239",
            password=service_password
        )
        admin_user = User(
            id=uuid.uuid4(),
            first_name="Admin",
            last_name="Account",
            email="admin@comp6239",
            password=admin_password,
            role="ADMIN"
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
        with self.db.session() as s:
            s.add(service_user)
            s.add(service_client)
            s.add(admin_user)
            s.commit()
            logging.info("Service Account: {} {}".format(service_user.email, service_password))
            logging.info("OAuth Client ID: {}".format(service_client.client_id))
            logging.info("Admin Account: {} {}".format(admin_user.email, admin_password))

    def run(self):
        """
        Run the result server
        """
        logging.info("Starting listen loop...")
        loop = asyncio.get_event_loop()
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
