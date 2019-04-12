import datetime
import os
import socket
from asyncio import sleep
from contextlib import closing
from multiprocessing import Process
from typing import Optional
from unittest import TestCase

import requests
from oauthlib.oauth2 import LegacyApplicationClient
from requests import Response
from requests_oauthlib import OAuth2Session

from backend import log
from backend.app import App

def get_free_port() -> int:
    with closing(socket.socket(socket.AF_INET, socket.SOCK_STREAM)) as s:
        s.bind(('', 0))
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        return s.getsockname()[1]


def launch_app(port):
    app = App(port)
    app.run()


class APITestCase(TestCase):
    api_uri = ""
    client = None  # type: Optional[OAuth2Session]
    test_time = datetime.datetime.utcnow().isoformat().lower()
    free_port = get_free_port()
    email = "test@test"
    password = "Test1!"

    @classmethod
    def get(cls, uri, json=None, query=None) -> Response:
        client = requests
        if cls.client is not None:
            client = cls.client
        return client.get(cls.api_uri + uri, json=json, params=query)

    @classmethod
    def post(cls, uri, json=None, query=None) -> Response:
        client = requests
        if cls.client is not None:
            client = cls.client
        return client.post(cls.api_uri + uri, json=json, params=query)

    @classmethod
    def put(cls, uri, json=None, query=None) -> Response:
        client = requests
        if cls.client is not None:
            client = cls.client
        return client.put(cls.api_uri + uri, json=json, params=query)

    @classmethod
    def delete(cls, uri, json=None, query=None) -> Response:
        client = requests
        if cls.client is not None:
            client = cls.client
        return client.delete(cls.api_uri + uri, json=json, params=query)

    @classmethod
    def setUpAPI(cls):
        cls.api_uri = "http://localhost:{}".format(cls.free_port)
        log.info("API URI: {}".format(cls.api_uri))
        cls.app_process = Process(target=launch_app, args=(cls.free_port,), daemon=True)
        cls.app_process.start()

        while True:
            try:
                requests.get(cls.api_uri + "/ping")
                break
            except requests.exceptions.ConnectionError:
                sleep(0.1)

    @classmethod
    def setUpClass(cls):
        cls.setUpAPI()
        os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "True"

    @classmethod
    def setUpOAuthClient(cls, username: str = None, password: str = None):
        if username is None:
            username = cls.email
        if password is None:
            password = cls.password
        with OAuth2Session(client=LegacyApplicationClient(client_id="7834452b-12ab-480d-9fc9-9f23b3546524")) as oauth:
            token = oauth.fetch_token(cls.api_uri + "/oauth/token", username=username, password=password)

            cls.client = OAuth2Session(
                client_id="7834452b-12ab-480d-9fc9-9f23b3546524",
                token=token,
                auto_refresh_url=cls.api_uri + "/oauth/token"
            )
