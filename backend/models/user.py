from uuid import UUID

from sqlalchemy.orm import Session

from backend.database import sql_session
from backend.models import User, UserRole


@sql_session
def user_exists_by_id(user_id: UUID, session: Session) -> bool:
    return session.query(User).filter_by(id=user_id).count() != 0


@sql_session
def user_exists_by_email(email: str, session: Session) -> bool:
    return session.query(User).filter_by(email=email).count() != 0


@sql_session
def user_is_role(id: UUID, role: UserRole, session: Session) -> bool:
    with session:
        user = get_user_by_id(id, session=session)
        return user.role == role


@sql_session
def get_user_by_email(email: str, session: Session, lock_update: bool = False) -> User:
    query = session.query(User).options(
        # noload(User.api_keys)
    ).filter_by(email=email)
    if lock_update:
        query = query.with_for_update()

    user = query.first()
    if user is None:
        return None
        # raise NotFoundException("User not found")
    return user


@sql_session
def get_user_by_id(id: UUID, session: Session, lock_update: bool = False) -> User:
    query = session.query(User).options(
        # noload(User.api_keys)
    ).filter_by(id=id)
    if lock_update:
        query = query.with_for_update()

    user = query.first()
    if user is None:
        return None
        # raise NotFoundException("User not found")
    return user
