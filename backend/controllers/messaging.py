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
    event_map = {}  # type: Dict[str, Union[callable, Coroutine]]

    def __init__(self, application, request, **kwargs):
        super().__init__(application, request, **kwargs)
        self.has_identified = False
        self.identify_task = None  # type: Optional[Future]

    @classmethod
    def add_handler(cls, event: Optional[Union[OpCode, str]] = None):
        def wrapper(f):
            if isinstance(event, OpCode):
                cls.method_map[event] = f
            elif isinstance(event, str):
                cls.event_map[event] = f

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

            result = self.method_map[payload.op](self, payload)
            if result is not None:
                await result

        except ValueError:
            self.send_opcode(OpCode.DECODE_ERROR)
            self.close()


@MessageSocket.add_handler(OpCode.IDENTIFY)
def identify(socket: MessageSocket, payload: Payload):
    if socket.has_identified:
        socket.send_opcode(OpCode.ALREADY_AUTHENTICATED)
        socket.close()
        return
    data = payload.data
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

    socket.send_payload(Payload.dispatch(
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


@MessageSocket.add_handler(OpCode.DISPATCH)
async def handle_dispatch(socket: MessageSocket, payload: Payload):
    if payload.event not in MessageSocket.method_map:
        return
    result = MessageSocket.method_map[payload.op](socket, payload)
    if result is not None:
        await result


@MessageSocket.add_handler("SEND_MESSAGE")
def send_message(socket: MessageSocket, payload: Payload):
    log.info("Send message received!")
    pass


async def identify_timeout(socket: MessageSocket, timeout: int = 45):
    await asyncio.sleep(timeout)
    if socket.has_identified:
        return
    if not socket.is_closed:
        log.info("Closing idle socket...")
        socket.close()
