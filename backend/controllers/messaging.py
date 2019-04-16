import asyncio
import time
import uuid
from asyncio import Future
from http import HTTPStatus
from typing import Union, Dict, Coroutine, List, Optional
from uuid import UUID

from sqlalchemy.orm import Session

from backend import log
from backend.controller import WebSocketController, Payload, OpCode, Controller
from backend.database import sql_session
from backend.exc import NotFoundException, AccessDeniedException
from backend.models import Message, UserRole, MessageThread, ThreadState, MessageState
from backend.models.messages import get_unread_thread_count, get_recent_threads, get_thread_by_user_ids, \
    get_thread_by_id, get_recent_messages_by_thread
from backend.models.user import get_user_by_id
from backend.oauth import server, protected
from backend.utils.regex import uuid as uuid_regex

connect_payload = Payload(
    OpCode.HELLO,
    {}
)


class MessageController(Controller):
    route = [r"/thread"]

    @protected(roles=[UserRole.STUDENT, UserRole.TUTOR])
    async def get(self):
        with self.app.db.session() as s:
            threads = get_recent_threads(self.current_user.id, session=s, number=None)

            content = []

            for thread in threads:
                if thread.student_id == self.current_user.id:
                    recipient = get_user_by_id(thread.tutor_id)
                else:
                    recipient = get_user_by_id(thread.student_id)

                m = thread.message

                state = thread.state
                if self.current_user.role == UserRole.STUDENT and state == ThreadState.BLOCKED:
                    state = ThreadState.REQUESTED

                content.append({
                    "id": thread.id,
                    "recipient": {
                        "id": recipient.id,
                        "first_name": recipient.first_name,
                        "last_name": recipient.last_name
                    },
                    "messages": {
                        "id": m.id,
                        "sender_id": m.sender_id,
                        "timestamp": m.created_at,
                        "message": m.message,
                        "state": m.state
                    },
                    "state": state
                })
            self.write(content)


class MessageThreadController(Controller):
    route = [r"/thread/(" + uuid_regex + ")"]

    @protected(roles=[UserRole.STUDENT, UserRole.TUTOR])
    async def get(self, thread_id: UUID):
        with self.app.db.session() as s:
            thread = get_thread_by_id(thread_id, session=s)

            if thread.student_id != self.current_user.id and thread.tutor_id != self.current_user.id:
                raise NotFoundException()

            state = thread.request_state
            if self.current_user.role == UserRole.STUDENT and state == ThreadState.BLOCKED:
                state = ThreadState.REQUESTED

            if thread.student_id == self.current_user.id:
                recipient = get_user_by_id(thread.tutor_id)
            else:
                recipient = get_user_by_id(thread.student_id)

            messages = get_recent_messages_by_thread(thread_id, session=s, number=None)

            self.write({
                "id": thread.id,
                "recipient": {
                    "id": recipient.id,
                    "first_name": recipient.first_name,
                    "last_name": recipient.last_name
                },
                "messages": [{
                    "id": m.id,
                    "sender_id": m.sender_id,
                    "timestamp": m.created_at,
                    "message": m.message,
                    "state": m.state
                } for m in messages],
                "state": state
            })


class MessageBlockRequestController(Controller):
    route = [r"/thread/(" + uuid_regex + ")/block"]

    @protected(roles=[UserRole.STUDENT, UserRole.TUTOR])
    async def post(self, thread_id: UUID):
        with self.app.db.session() as s:
            thread = get_thread_by_id(thread_id, session=s, lock_update=True)

            if thread.student_id != self.current_user.id and thread.tutor_id != self.current_user.id:
                raise NotFoundException()

            thread.request_state = ThreadState.BLOCKED

            s.add(thread)
            s.commit()
        self.set_status(HTTPStatus.NO_CONTENT)


class MessageApproveRequestController(Controller):
    route = [r"/thread/(" + uuid_regex + ")/approve"]

    @protected(roles=[UserRole.STUDENT, UserRole.TUTOR])
    async def post(self, thread_id: UUID):
        with self.app.db.session() as s:
            thread = get_thread_by_id(thread_id, session=s, lock_update=True)

            if thread.student_id != self.current_user.id and thread.tutor_id != self.current_user.id:
                raise NotFoundException()

            if self.current_user.role != UserRole.TUTOR:
                raise AccessDeniedException()

            thread.request_state = ThreadState.ALLOWED

            s.add(thread)
            s.commit()
        self.set_status(HTTPStatus.NO_CONTENT)


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

    unread_thread_count = get_unread_thread_count(user.id)
    recent_threads = get_recent_threads(user.id)
    threads = []
    for thread in recent_threads:
        state = thread.request_state
        if user.role == UserRole.STUDENT:
            recipient_id = thread.tutor_id
            if state == ThreadState.BLOCKED:
                state = ThreadState.REQUESTED
        else:
            recipient_id = thread.student_id
        recipient = get_user_by_id(recipient_id)

        threads.append({
            "id": thread.id,
            "recipient": {
                "id": recipient.id,
                "first_name": recipient.first_name,
                "last_name": recipient.last_name
            },
            "messages": [
                {
                    "id": thread.message.id,
                    "sender_id": thread.message.sender_id,
                    "message": thread.message.message,
                    "state": thread.message.state,
                    "timestamp": thread.message.created_at
                }
            ],
            "state": state
        })

    socket.send_payload(Payload.dispatch(
        "READY",
        {
            "id": user.id,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "unread_threads": unread_thread_count,
            "recent_threads": threads
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

    if sender.role == UserRole.STUDENT:
        student = sender
        tutor = recipient
        thread = get_thread_by_user_ids(student_id=sender.id, tutor_id=recipient.id, session=session)
    else:
        student = recipient
        tutor = sender
        thread = get_thread_by_user_ids(student_id=recipient.id, tutor_id=sender.id, session=session)

    if thread is None:
        is_new_thread = True
        if sender.role != UserRole.STUDENT:
            log.warning("Not allowing non-student to send first message")
            return

        thread = MessageThread(
            id=uuid.uuid4(),
            student_id=student.id,
            tutor_id=tutor.id,
        )
        session.add(thread)
    else:
        is_new_thread = False
        if thread.request_state == ThreadState.BLOCKED:
            log.warning("Not sending message as thread is blocked!")
            return

    message = Message(
        id=uuid.uuid1(int(time.time())),
        sender_id=sender.id,
        thread_id=thread.id,
        message=data["message"]
    )
    thread.state = MessageState.SENT

    session.add(message)
    session.commit()

    # TODO: send message with FCM
    if is_new_thread:
        event_type = "MESSAGE_REQUEST"
    else:
        event_type = "MESSAGE"

    if not is_new_thread and thread.request_state != ThreadState.ALLOWED:
        log.info("Not broadcasting message")
        return

    socket.broadcast(
        recipient.id,
        Payload.dispatch(
            event_type,
            {
                "thread_id": thread.id,
                "from": {
                    "id": sender.id,
                    "first_name": sender.first_name,
                    "last_name": sender.last_name
                },
                "message": message.message,
                "timestamp": message.created_at
            }
        )
    )
    log.info("Sent message to {}".format(recipient.id))


async def identify_timeout(socket: MessageSocket, timeout: int = 45):
    await asyncio.sleep(timeout)
    if socket.has_identified:
        return
    if not socket.is_closed:
        log.info("Closing idle socket...")
        socket.close()
