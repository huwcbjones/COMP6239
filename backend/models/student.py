from typing import List
from uuid import UUID

from sqlalchemy.orm import Session

from backend.database import sql_session
from backend.models import Student, Subject


@sql_session
def get_student_by_id(id: UUID, session: Session, lock_update: bool = False) -> Student:
    query = session.query(Student).options(

    ).filter_by(id=id)
    if lock_update:
        query = query.with_for_update()

    user = query.first()
    if user is None:
        return None
        # raise NotFoundException("User not found")
    return user


@sql_session
def get_subjects_by_student_id(id: UUID, session: Session) -> List[Subject]:
    query = session.query(Subject).join(Subject.students).filter_by(id=id)

    user = query.all()
    if user is None:
        return None
        # raise NotFoundException("User not found")
    return user
