import http.client
import json
import logging
from json import JSONDecodeError
from typing import Dict

import tornado.web
import tornado.websocket

from backend.exc import BadRequestException
from backend.utils.json import dumps


class Controller(tornado.web.RequestHandler):
    """
    Controller
    Attributes:
        json_args (Dict): JSON Data
    """

    route = None
    app = None

    def __init__(self, application, request, **kwargs):
        self.json_args = None
        super().__init__(application, request, **kwargs)

    def prepare(self):
        headers = self.request.headers
        self.json_args = {}
        if "Content-Type" in headers and headers["Content-Type"].startswith("application/json"):
            try:
                self.json_args = json.loads(self.request.body)
            except JSONDecodeError as e:
                logging.warning(e.msg)
                raise tornado.web.HTTPError(400, reason="Could not parse JSON data.")

    def write_error(self, status_code, **kwargs):
        info = kwargs.get("exc_info")
        try:
            if info is not None and len(info) > 2 and hasattr(info[1], "message") and info[1].message is not None:
                self.write({"message": info[1].message})
            else:
                self.write({"message": http.client.responses[status_code]})
        except TypeError:
            self.write({"message": http.client.responses[status_code]})

    def write(self, chunk, set_content_type=True, status_code=None):
        if status_code is not None:
            self.set_status(status_code)
        if chunk is None:
            return
        if isinstance(chunk, (dict, list)):
            chunk = dumps(chunk)
        # if isinstance(chunk, (Model, dict, list)):
        #     chunk = json.dumps(chunk, cls=ModelDecoder)
        if set_content_type:
            self.set_header('Content-Type', 'application/json')
        super().write(chunk)

    def check_required_fields(self, *fields):
        missing_fields = [f for f in fields if f not in self.json_args]

        if not missing_fields:
            return
        raise BadRequestException(
            "Missing following required field(s): {}".format(
                ", ".join(missing_fields)
            )
        )

    def get_valid_fields(self, *fields) -> Dict:
        return {k: v for k, v in self.json_args.items() if k in fields}


class WebSocketController(tornado.websocket.WebSocketHandler):
    """
    SwimSuite Controller
    Attributes:
        app (Result): The app instance
    """
    app = None
    route = None

    def __init__(self, application, request, **kwargs):
        super().__init__(application, request, **kwargs)

    def check_origin(self, origin):
        if __debug__:
            return True
        return super().check_origin(origin)

    def write_message(self, message, binary=False):
        if isinstance(message, (dict, list)):
            message = dumps(message)
        super().write_message(message, binary)
