from typing import List
from uuid import UUID

from sqlalchemy.orm import Session

from backend.database import sql_session
from backend.models import Subject


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
