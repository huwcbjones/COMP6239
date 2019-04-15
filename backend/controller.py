import http.client
import json
import logging
import re
from json import JSONDecodeError
from typing import Dict, Any, Optional, Union, List

from tornado.log import gen_log
from tornado.web import RequestHandler, HTTPError
from tornado.websocket import WebSocketHandler, WebSocketClosedError

from backend.exc import BadRequestException
from backend.models import User
from backend.utils import enum
from backend.utils.json import dumps


class Controller(RequestHandler):
    """
    Controller
    Attributes:
        json_args (Dict): JSON Data
    """

    route = None
    app = None

    def __init__(self, application, request, **kwargs):
        self.current_user = None  # type: Optional[User]
        self.json_args = None
        self.options = {}  # type: Dict
        self.remote_ip = request.remote_ip  # type: str
        super().__init__(application, request, **kwargs)

    def prepare(self):
        headers = self.request.headers
        self.json_args = {}
        if "Content-Type" in headers and headers["Content-Type"].startswith("application/json"):
            try:
                self.json_args = json.loads(self.request.body)
            except JSONDecodeError as e:
                logging.warning(e.msg)
                raise HTTPError(400, reason="Could not parse JSON data.")
        self._parse_common_options()

    def write_error(self, status_code, **kwargs):
        info = kwargs.get("exc_info")
        try:
            if info is not None and len(info) > 2 and hasattr(info[1], "message") and info[1].message is not None:
                self.write({"message": info[1].message})
            else:
                self.write({"message": http.client.responses[status_code]})
        except TypeError:
            self.write({"message": http.client.responses[status_code]})

    def log_exception(self, typ, value, tb):
        if isinstance(value, HTTPError) and value.log_message:
            format = "%d %s: " + value.log_message
            args = ([value.status_code, self._request_summary()] +
                    list(value.args))
            gen_log.warning(format, *args)
        else:
            gen_log.exception(value)

    def write(self, chunk: Any, set_content_type=True, status_code=None):
        if status_code is not None:
            self.set_status(status_code)
        if chunk is None:
            return
        if isinstance(chunk, (dict, list)):
            if isinstance(chunk, dict):
                chunk = dict(sorted(chunk.items()))
            chunk = dumps(chunk)
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

    def merge_fields(self, object, *fields):
        for f in fields:
            if not hasattr(object, f):
                continue
            if f not in self.json_args:
                continue
            if getattr(object, f) == self.json_args[f]:
                continue
            setattr(object, f, self.json_args[f])

    def get_valid_fields(self, *fields) -> Dict:
        return {k: v for k, v in self.json_args.items() if k in fields}

    def _parse_common_options(self):
        self.options = {"page": 1, "per_page": 50}
        for k in ["page", "per_page"]:
            if k in self.request.arguments:
                try:
                    self.options[k] = int(self.request.arguments[k][0])
                except Exception:
                    raise BadRequestException("Invalid value for parameter {}".format(k))

        self.options["search"] = self.get_argument("search", "")
        self.options["filter"] = parse_filter_option(self.get_query_argument("filter", ""))

        fields = {}
        if "sort" in self.request.arguments:
            sorts = self.get_arguments("sort")
            for sort in sorts:
                parts = sort.split(",")
                for part in parts:
                    if part.strip() == "":
                        continue
                    pieces = part.split("|")
                    fields[pieces[0]] = pieces[1]
        self.options["sort"] = fields

    def _request_summary(self):
        return "{} {} ({})".format(self.request.method, self.request.uri, self.remote_ip)


class OpCode(enum.Enum):
    DISPATCH = 0
    IDENTIFY = 2
    INVALID_SESSION = 9
    HELLO = 10

    UNKNOWN_ERROR = 4000
    UNKNOWN_OPCODE = 4001
    DECODE_ERROR = 4002
    NOT_AUTHENTICATED = 4003
    AUTHENTICATION_FAILED = 4004
    ALREADY_AUTHENTICATED = 4005
    RATE_LIMITED = 4008
    SESSION_TIMEOUT = 4009


class Payload:

    def __init__(self, op_code: OpCode, data: Optional[dict], event: Optional[str] = None):
        self.op = op_code
        self.data = data
        self.event = event
        if self.event is not None:
            self.event = self.event.upper()

    def serialise(self) -> bytes:
        data = {
            "o": self.op.value,
            "d": self.data,
            "e": self.event
        }
        payload = dumps(data)
        return payload.encode()

    @classmethod
    def deserialise(cls, data: Union[bytes, str]) -> "Payload":
        if isinstance(data, bytes):
            data = data.decode()
        payload = json.loads(data)
        if "o" not in payload or "d" not in payload:
            raise ValueError

        if not OpCode.contains(payload["o"]):
            raise ValueError("Invalid OpCode: {}".format(payload["o"]))

        op_code = OpCode(payload["o"])

        event = None
        if op_code == OpCode.DISPATCH:
            if "e" not in payload:
                raise ValueError("Missing event type")
            event = payload["e"].upper()

        payload = payload["d"]

        if not isinstance(payload, (dict, list)):
            payload = json.loads(payload)

        return Payload(op_code, payload, event=event)

    def __repr__(self):
        if self.op == OpCode.DISPATCH:
            return "{}: {}".format(self.event, dumps(self.data))
        else:
            return "{}: {}".format(self.op.name, dumps(self.data))

    @classmethod
    def dispatch(cls, event: str, data: Union[Dict, List]) -> "Payload":
        return Payload(
            OpCode.DISPATCH,
            data,
            event
        )


class WebSocketController(WebSocketHandler):
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

    def write_message(self, message: Union[bytes, str, Dict[str, Any]], binary=False):
        if isinstance(message, (dict, list)):
            message = dumps(message)
        super().write_message(message, binary)

    def send_payload(self, payload: Payload):
        try:
            self.write_message(payload.serialise())
        except WebSocketClosedError:
            pass

    def send_opcode(self, opcode: OpCode):
        try:
            payload = Payload(opcode, {})
            self.write_message(payload.serialise())
        except WebSocketClosedError:
            pass

    @property
    def is_closed(self):
        return self.close_code is not None and self.close_reason is not None


def parse_multi_field_option(string: str, arg_separator: str = "|", param_separator: str = ":") -> Dict[str, Any]:
    """
    Parse a multi-field value into a key=>value pairs
    Example string: location:Hampshire|subject:Biology,Chemistry
    Would be resolved into:
        {
            "location": "Hampshire",
            "subject": [
                "Biology",
                "Chemistry"
            ]
        }
    :param string: String to parse
    :param arg_separator: Separator between arguments (k=>v pairs)
    :param param_separator: Separator between parameter (key and value)
    :return:
    """
    fields = {}
    parts = string.split(arg_separator)
    for part in parts:
        if part.strip() == "":
            continue
        pieces = part.split(param_separator)
        if len(pieces) == 2:
            field = pieces[0]
            value = pieces[1]
            if "," in value:
                value = value.split(",")
            fields[field] = value

    return fields


def parse_filter_option(string: str, arg_separator: str = " ") -> Dict[str, Dict[str, Any]]:
    """
    Parse a filter into a key=>value pairs
    Example string: ip:1.2.3.4 fqdn:host.local
    Would be resolved into:
        {
            "location": {
                "value": "Hampshire",
                "operator": "="
            },
            "subject": {
                "value": ["Biology", "Chemistry"],
                "operator": "="
            },
        }
    :param string: String to parse
    :param arg_separator: Separator between arguments (k=>v pairs)
    :return:
    """
    fields = {}  # type: Dict[str, Dict[str, Any]]
    parts = string.split(arg_separator)
    parser = re.compile(r"(\w+)([<>!=:]+)([^\n]*)")
    for part in parts:
        if part.strip() == "":
            continue
        pieces = [p for p in parser.split(part) if p.strip() != ""]
        if len(pieces) == 3:
            key, operator, value = pieces[:3]
            if operator == ":":
                operator = "="
            if value.lower() == "true":
                value = True
            elif value.lower() == "false":
                value = False
            elif re.match(r"[0-9]+", value):
                try:
                    value = int(value)
                except (TypeError, ValueError):
                    pass
            else:
                value = value.strip()
            fields[key] = {
                "operator": operator,
                "value": value
            }
    return fields
