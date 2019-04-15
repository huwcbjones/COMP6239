import asyncio
import time
import uuid
from asyncio import Future
from typing import Union, Dict, Coroutine, List, Optional
from uuid import UUID

from sqlalchemy.orm import Session

from backend import log
from backend.controller import WebSocketController, Payload, OpCode
from backend.database import sql_session
from backend.models import Message, UserRole
from backend.models.user import get_user_by_id
from backend.oauth import server

connect_payload = Payload(
    OpCode.HELLO,
    {}
)


class MessageSocket(WebSocketController):
    route = [r"/ws"]
    method_map = {}  # type: Dict[OpCode, Union[callable, Coroutine]]
    event_map = {}  # type: Dict[str, Union[callable, Coroutine]]

    client_maps = {}  # type: Dict[UUID, List[MessageSocket]]

    def __init__(self, application, request, **kwargs):
        super().__init__(application, request, **kwargs)
        self._has_identified = False
        self.identify_task = None  # type: Optional[Future]

    @property
    def has_identified(self) -> bool:
        return self._has_identified

    @has_identified.setter
    def has_identified(self, value: bool):
        self._has_identified = value
        if not value:
            return
        user_id = self.current_user.id
        if user_id not in self.client_maps:
            self.client_maps[user_id] = list()
        self.client_maps[user_id].append(self)

    @classmethod
    def add_handler(cls, event: Optional[Union[OpCode, str]] = None):
        def wrapper(f):
            if isinstance(event, OpCode):
                cls.method_map[event] = f
            elif isinstance(event, str):
                cls.event_map[event] = f

        return wrapper

    def broadcast(self, user_id: UUID, payload: Payload):
        if user_id not in self.client_maps:
            return
        [c.send_payload(payload) for c in self.client_maps[user_id]]

    def open(self, *args: str, **kwargs: str):
        self.send_payload(connect_payload)
        self.identify_task = asyncio.ensure_future(identify_timeout(self))

    def on_close(self) -> None:
        super().on_close()

        if not self.has_identified:
            return

        user_id = self.current_user.id
        if user_id not in self.client_maps:
            return

        if self in self.client_maps[user_id]:
            self.client_maps[user_id].remove(self)

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
    if user.role == UserRole.ADMIN:
        socket.send_opcode(OpCode.INVALID_SESSION)
        socket.close()
        return

    socket.current_user = user
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
    if payload.event not in MessageSocket.event_map:
        return
    result = MessageSocket.event_map[payload.event](socket, payload)
    if result is not None:
        await result


@MessageSocket.add_handler("SEND_MESSAGE")
@sql_session
def send_message(socket: MessageSocket, payload: Payload, session: Session):
    data = payload.data
    if "to" not in data or "message" not in data:
        return

    sender = get_user_by_id(socket.current_user.id, session)
    recipient = get_user_by_id(data["to"], session)
    if not recipient:
        log.info("Not sending message to {} - does not exist".format(data["to"]))
        return

    if recipient.role == sender.role:
        log.info("Not sending message to {} - cannot send message to users of same role ({})".format(
            data["to"], recipient.role
        ))
        return

    message = Message(
        id=uuid.uuid1(int(time.time())),
        from_id=sender.id,
        to_id=recipient.id,
        message=data["message"]
    )

    with session as s:  # type: Session
        s.add(message)
        s.commit()

    # TODO: send message with FCM
    # TODO: prevent tutors from messaging students first
    # TODO: add message request before unfiltered communication
    socket.broadcast(
        recipient.id,
        Payload.dispatch(
            "MESSAGE",
            {
                "from": {
                    "id": sender.id,
                    "first_name": sender.first_name,
                    "last_name": sender.last_name
                },
                "message": message.message,
                "timestamp": message.created_at.utcnow()
            }
        )
    )
    log.info("Sent message to {}".format(message.to_id))


async def identify_timeout(socket: MessageSocket, timeout: int = 45):
    await asyncio.sleep(timeout)
    if socket.has_identified:
        return
    if not socket.is_closed:
        log.info("Closing idle socket...")
        socket.close()
