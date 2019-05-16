from typing import List
from uuid import UUID

from sqlalchemy import func, or_
from sqlalchemy.orm import Session, joinedload

from backend.database import sql_session
from backend.models import TutorProfile, Tutor, Subject, MessageThread, ThreadState, User, UserRole
from backend.models.messages import get_recent_messages_by_thread
from backend.models.user import get_user_by_id


@sql_session
def get_tutors(session: Session, include_unapproved: bool = False) -> List[Tutor]:
    with session:
        subquery = session.query(
            func.max(TutorProfile.id)
        ).group_by(TutorProfile.tutor_id)
        if not include_unapproved:
            subquery = subquery.filter(TutorProfile.reason.is_(None)).filter(TutorProfile.reviewed_at.isnot(None))
        query = session.query(TutorProfile).options(
            joinedload(TutorProfile.tutor),
            joinedload(TutorProfile.subjects)
        ).filter(TutorProfile.id.in_(subquery))
        tutors = query.all()
        return [Tutor(p.tutor, p) for p in tutors]


@sql_session
def get_unapproved_tutors(session: Session) -> List[Tutor]:
    with session:
        subquery = session.query(
            func.max(TutorProfile.id)
        ).group_by(TutorProfile.tutor_id).filter(
            TutorProfile.bio.isnot(None),
            TutorProfile.price.isnot(None),
            TutorProfile.reason.is_(None),
            TutorProfile.reviewed_at.is_(None)
        )
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
def get_profile_by_tutor_id(id: UUID, session: Session, is_approved: bool = False) -> TutorProfile:
    with session:
        query = session.query(TutorProfile).options(
            joinedload(TutorProfile.subjects)
        ).filter_by(tutor_id=id).order_by(TutorProfile.id.desc())
        if is_approved:
            query = query.filter(TutorProfile.reviewed_at.isnot(None))
        return query.first()


@sql_session
def get_tutor_by_id(id: UUID, session: Session, lock_update: bool = False, is_approved: bool = False) -> Tutor:
    if id is None:
        return None
    with session:
        user = get_user_by_id(id, session, lock_update=lock_update)
        if user is None:
            return None
        profile = get_profile_by_tutor_id(id, session, is_approved=is_approved)
        if profile is None:
            return None
        return Tutor(user, profile)


@sql_session
def get_subjects_by_tutor_id(id: UUID, session: Session, is_approved: bool = False) -> List[Subject]:
    profile_id = get_profile_by_tutor_id(id, session=session, is_approved=is_approved).id
    query = session.query(Subject).join(Subject.tutors).filter_by(id=profile_id)
    subjects = query.all()
    if subjects is None:
        return None
        # raise NotFoundException("User not found")
    return subjects


@sql_session
def get_tutees_threads_by_tutor_id(tutor_id: UUID, session: Session) -> List[MessageThread]:
    query = session.query(
        MessageThread
    ).filter_by(
        tutor_id=tutor_id,
        request_state=ThreadState.ALLOWED
    ).options(
        joinedload(MessageThread.student),
        joinedload(MessageThread.tutor)
    )

    threads = query.all()
    for t in threads:
        t.messages = get_recent_messages_by_thread(thread_id=t.id, session=session, page_size=2)

    return threads


@sql_session
def get_tutee_request_threads_by_tutor_id(tutor_id: UUID, session: Session) -> List[MessageThread]:
    query = session.query(
        MessageThread
    ).filter_by(
        tutor_id=tutor_id,
        request_state=ThreadState.REQUESTED
    ).options(
        joinedload(MessageThread.student),
        joinedload(MessageThread.tutor)
    )

    threads = query.all()
    for t in threads:
        t.messages = get_recent_messages_by_thread(thread_id=t.id, session=session, page_size=1)

    return threads


@sql_session
def search_tutors(
        name: str = None,
        location: str = None,
        price_lower: int = None,
        price_higher: int = None,
        subjects: List[str] = None,
        query_str: str = None,
        session: Session = None
) -> List[Tutor]:
    query = session.query(User.id).filter_by(role=UserRole.TUTOR)
    if name:
        query = query.filter(or_(
            User.first_name.ilike("%{}%".format(name)),
            User.last_name.ilike("%{}%".format(name))
        ))

    if location:
        query = query.filter(User.location.ilike("%{}%".format(location)))

    if query_str:
        subjects = [s[0] for s in session.query(Subject.id).filter(Subject.name.ilike("%" + query_str + "%")).all()]
        if not subjects:
            query = query.filter(or_(
                User.first_name.ilike("%{}%".format(query_str)),
                User.last_name.ilike("%{}%".format(query_str)),
                User.location.ilike("%{}%".format(query_str)),
            ))

    valid_tutor_ids = set([i[0] for i in query.all()])
    query = session.query(TutorProfile.tutor_id, func.max(TutorProfile.id)).group_by(TutorProfile.tutor_id).filter(
        TutorProfile.reviewed_at.isnot(None),
        TutorProfile.reason.is_(None)
    )
    if subjects:
        query = query.filter(TutorProfile.subjects.any(Subject.id.in_(subjects)))

    if price_lower:
        query = query.filter(TutorProfile.price >= price_lower)
    if price_higher:
        query = query.filter(TutorProfile.price <= price_higher)
    valid_tutor_profile_ids = set([i[0] for i in query.all()])

    tutor_ids = valid_tutor_ids.intersection(valid_tutor_profile_ids)
    return [get_tutor_by_id(i) for i in tutor_ids]
