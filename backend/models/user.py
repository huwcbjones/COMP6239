from typing import Dict, Any, Union, List
from uuid import UUID

from sqlalchemy.orm import Session

# from models import User, apply_common_options, get_pagination_data
# from utils import sql, convert_to_uuid
# from utils.exceptions import NotFoundException
# from utils.sql import handle_db_error, sql_session
from backend.database import sql_session
from backend.models import User, Student, Subject, student_subject_assoc_table


# @handle_db_error
# @sql_session
# def user_exists(user_id, session):
    # type: (Union[int, UUID], Session) -> bool
    # user_id = convert_to_uuid(user_id)
    # return session.query(User.id).filter_by(id=user_id).count() != 0


# @handle_db_error
# @sql_session
# def get_users(options, session):
    # type: (Dict[str, Any], Session) -> Dict[str, Any]
    # query = session.query(User)
    # total = query.count()
    # query = apply_common_options(query, User, options)
    #
    # users = query.all()
    # if users is None:
    #     users = []
    # data = get_pagination_data(options, total)
    # data['data'] = users
    # return data


@sql_session
def user_exists_by_id(user_id: UUID, session: Session) -> bool:
    return session.query(User).filter_by(id=user_id).count() != 0


@sql_session
def user_exists_by_email(email: str, session: Session) -> bool:
    return session.query(User).filter_by(email=email).count() != 0


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
    query = session.query(student_subject_assoc_table).join(Subject).filter(Student.id==id)

    user = query.all()
    if user is None:
        return None
        # raise NotFoundException("User not found")
    return user