import asyncio
from asyncio import Future
from typing import Union, Dict, Coroutine, List, Optional

from backend import log
from backend.controller import WebSocketController, Payload, OpCode
from backend.oauth import server

connect_payload = Payload(
    OpCode.HELLO,
    {}
)


class MessageSocket(WebSocketController):
    route = [r"/ws"]
    method_map = {}  # type: Dict[OpCode, Union[callable, Coroutine]]

    def __init__(self, application, request, **kwargs):
        super().__init__(application, request, **kwargs)
        self.has_identified = False
        self.identify_task = None  # type: Optional[Future]

    @classmethod
    def add_handler(cls, op=None):
        def wrapper(f):
            cls.method_map[op] = f

        return wrapper

    def open(self, *args: str, **kwargs: str):
        self.send_payload(connect_payload)
        self.identify_task = asyncio.ensure_future(identify_timeout(self))

    async def on_message(self, message: Union[str, bytes]):
        try:
            payload = Payload.deserialise(message)
            log.info("Received payload: '{}'".format(payload))

            if not self.has_identified and payload.op != OpCode.IDENTIFY:
                self.send_opcode(OpCode.NOT_AUTHENTICATED)
                self.close()
                return

            if payload.op not in self.method_map:
                self.send_opcode(OpCode.UNKNOWN_OPCODE)
                self.close()
                return

            result = self.method_map[payload.op](self, payload.data)
            if result is not None:
                await result(self, payload.data)

        except ValueError:
            self.send_opcode(OpCode.DECODE_ERROR)
            self.close()


@MessageSocket.add_handler(OpCode.IDENTIFY)
def identify(socket: MessageSocket, data: Union[Dict, List]):
    if socket.has_identified:
        socket.send_opcode(OpCode.ALREADY_AUTHENTICATED)
        socket.close()
        return

    if "properties" not in data:
        socket.send_opcode(OpCode.INVALID_SESSION)
        socket.close()
        return

    properties = {}
    for f in ("os", "device"):
        if f not in data["properties"]:
            socket.send_opcode(OpCode.INVALID_SESSION)
            socket.close()
            return
        properties[f] = data["properties"][f]

    socket.properties = properties

    log.info("Hello from: {}".format(data))
    if "token" not in data:
        socket.send_opcode(OpCode.INVALID_SESSION)
        socket.close()
        return

    token = data["token"]
    if "Authorization" not in socket.request.headers:
        socket.request.headers["Authorization"] = "Bearer " + token
    v, r = server.verify_request(
        socket.request.uri,
        http_method=socket.request.method,
        body=socket.request.body,
        headers=socket.request.headers,
        scopes=""
    )
    if not v:
        socket.send_opcode(OpCode.INVALID_SESSION)
        socket.close()
        return
    user = r.user
    socket.has_identified = True
    if socket.identify_task:
        socket.identify_task.cancel()

    socket.send_payload(Payload.event(
        "READY",
        {
            "id": user.id,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "unread_threads": 0,
            "recent_threads": [
                {}
            ]
        }
    ))


async def identify_timeout(socket: MessageSocket, timeout: int = 45):
    await asyncio.sleep(timeout)
    if socket.has_identified:
        return
    if not socket.is_closed:
        log.info("Closing idle socket...")
        socket.close()
