from typing import List
from uuid import UUID

from sqlalchemy import func
from sqlalchemy.orm import Session, joinedload

from backend.database import sql_session
from backend.models import TutorProfile, Tutor
from backend.models.user import get_user_by_id


@sql_session
def get_tutors(session: Session, include_unapproved: bool = False) -> List[Tutor]:
    with session:
        subquery = session.query(
            func.max(TutorProfile.id)
        ).group_by(TutorProfile.tutor_id)
        if not include_unapproved:
            subquery = subquery.filter(TutorProfile.approved_at.isnot(None))
        query = session.query(TutorProfile).options(
            joinedload(TutorProfile.tutor),
            joinedload(TutorProfile.subjects)
        ).filter(TutorProfile.id.in_(subquery))
        tutors = query.all()
        return [Tutor(p.tutor, p) for p in tutors]


@sql_session
def profile_exists_by_id(profile_id: int, session: Session) -> bool:
    return session.query(TutorProfile).filter_by(id=profile_id).count() != 0


@sql_session
def get_profile_by_id(id: UUID, session: Session) -> TutorProfile:
    with session:
        query = session.query(TutorProfile).options(
        ).filter_by(tutor_id=id).order_by(TutorProfile.id.desc())
        return query.first()


@sql_session
def get_tutor_by_id(id: UUID, session: Session) -> Tutor:
    with session:
        user = get_user_by_id(id, session)
        profile = get_profile_by_id(id, session)
        return Tutor(user, profile)
