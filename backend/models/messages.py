from typing import List, Optional
from uuid import UUID

from sqlalchemy import func, and_, or_
from sqlalchemy.orm import Session, Query

from backend.database import sql_session
from backend.models import Message, MessageThread, MessageState


@sql_session
def get_recent_threads(user_id: UUID, session: Session, number: Optional[int] = 10) -> List[MessageThread]:
    thread_query = session.query(MessageThread).filter(or_(
        MessageThread.tutor_id == user_id, MessageThread.student_id == user_id
    )).order_by(MessageThread.modified_at.desc())

    if number is not None:
        thread_query = thread_query.limit(number)
    threads = thread_query.all()

    for thread in threads:
        message = get_recent_messages_by_thread(thread.id, session=session, page_size=1)[0]
        thread.message = message

    return threads


@sql_session
def get_thread_by_user_ids(student_id: UUID, tutor_id: UUID, session: Session) -> MessageThread:
    query = session.query(MessageThread).filter(
        MessageThread.student_id == student_id,
        MessageThread.tutor_id == tutor_id
    )  # type: Query
    return query.one_or_none()


@sql_session
def get_thread_by_id(thread_id: UUID, session: Session, lock_update: bool = False) -> MessageThread:
    query = session.query(MessageThread).filter_by(id=thread_id)  # type: Query
    if lock_update:
        query = query.with_for_update()

    return query.first()


@sql_session
def get_recent_messages_by_thread(thread_id: UUID, session: Session, page: Optional[int] = 0, page_size: Optional[int] = 10) -> List[Message]:
    query = session.query(Message).filter_by(thread_id=thread_id).order_by(Message.created_at.desc())  # type: Query

    if page_size:
        query = query.limit(page_size)
        if page:
            query = query.offset(page * page_size)

    return query.all()


@sql_session
def get_unread_thread_count(user_id: UUID, session: Session) -> int:
    query = session.query(func.count(MessageThread.id)).filter(
        and_(
            MessageThread.state != MessageState.READ, or_(
                MessageThread.student_id == user_id,
                MessageThread.tutor_id == user_id
            )
        )
    )  # type: Query
    return query.first()[0]
