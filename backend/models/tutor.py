from typing import List
from uuid import UUID

from sqlalchemy.orm import Session, joinedload

from backend.database import sql_session
from backend.models import TutorProfile, Tutor
from backend.models.user import get_user_by_id


@sql_session
def get_tutors(session: Session) -> List[TutorProfile]:
    with session:
        query = session.query(TutorProfile).options(
            joinedload(TutorProfile.tutor)
        )
        return query.all()


@sql_session
def profile_exists_by_id(profile_id: UUID, session: Session) -> bool:
    return session.query(TutorProfile).filter_by(id=profile_id).count() != 0


@sql_session
def get_profile_by_id(id: UUID, session: Session) -> TutorProfile:
    with session:
        query = session.query(TutorProfile).options(
        ).filter_by(tutor_id=id).order_by(TutorProfile.revision.desc())
        return query.first()


@sql_session
def get_tutor_by_id(id: UUID, session: Session) -> Tutor:
    with session:
        user = get_user_by_id(id, session)
        profile = get_profile_by_id(id, session)
        return Tutor(user, profile)
