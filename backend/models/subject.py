from typing import List
from uuid import UUID

from sqlalchemy.orm import Session, joinedload

from backend.database import sql_session
from backend.models import Subject, MessageThread, ThreadState
from backend.models.messages import get_recent_messages_by_thread


@sql_session
def get_subjects(session: Session) -> List[Subject]:
    with session:
        subjects = session.query(Subject).order_by(Subject.name).all()
        return subjects or []


@sql_session
def subject_exists_by_id(id: UUID, session: Session) -> bool:
    with session:
        return session.query(Subject).filter_by(id=id).count() != 0


@sql_session
def subject_exists_by_name(name: str, session: Session) -> bool:
    with session:
        return session.query(Subject).filter_by(name=name).count() != 0


@sql_session
def get_subject_by_id(id: UUID, session: Session, lock_update: bool = False) -> Subject:
    with session:
        query = session.query(Subject).options(
        ).filter_by(id=id)
        if lock_update:
            query = query.with_for_update()

        subject = query.first()
        if subject is None:
            return None
            # raise NotFoundException("User not found")
        return subject


@sql_session
def get_tutor_threads_by_student_id(student_id: UUID, session: Session) -> List[MessageThread]:
    query = session.query(
        MessageThread
    ).filter_by(
        student_id=student_id,
        request_state=ThreadState.ALLOWED
    ).options(
        joinedload(MessageThread.student),
        joinedload(MessageThread.tutor)
    )

    threads = query.all()
    for t in threads:
        t.messages = get_recent_messages_by_thread(thread_id=t.id, session=session, page_size=1)

    return query.all()


@sql_session
def get_tutor_request_threads_by_student_id(student_it: UUID, session: Session) -> List[MessageThread]:
    query = session.query(
        MessageThread
    ).filter_by(
        student_id=student_it,
        request_state=ThreadState.REQUESTED
    ).options(
        joinedload(MessageThread.student),
        joinedload(MessageThread.tutor)
    )

    threads = query.all()
    for t in threads:
        t.messages = get_recent_messages_by_thread(thread_id=t.id, session=session, page_size=1)

    return query.all()
