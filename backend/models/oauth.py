import uuid
from datetime import timedelta, datetime
from typing import List
from uuid import UUID

from sqlalchemy.orm import Session, joinedload

from backend.database import sql_session
from backend.models import OAuthClient, OAuthGrantToken, OAuthBearerToken, User


@sql_session
def client_exists_by_id(client_id: UUID, session: Session) -> bool:
    return session.query(OAuthClient).filter_by(id=client_id).count() != 0


@sql_session
def get_client_by_id(client_id: UUID, session: Session, lock_update: bool = False) -> OAuthClient:
    query = session.query(OAuthClient).options(
        joinedload(OAuthClient.user)
    ).filter_by(id=client_id)
    if lock_update:
        query = query.with_for_update()

    client = query.first()
    if client is None:
        return None
        # raise NotFoundException("User not found")
    return client


@sql_session
def grant_token_exists_by_id(grant_id: UUID, session: Session) -> bool:
    return session.query(OAuthGrantToken).filter_by(id=grant_id).count() != 0


@sql_session
def get_grant_token_by_id(grant_id: UUID, session: Session, lock_update: bool = False) -> OAuthGrantToken:
    query = session.query(OAuthGrantToken).options(
        # noload(User.api_keys)
    ).filter_by(id=grant_id)
    if lock_update:
        query = query.with_for_update()

    token = query.first()
    if token is None:
        return None
        # raise NotFoundException("User not found")
    return token


@sql_session
def get_grant_token_by_code(code: str, session: Session, lock_update: bool = False) -> OAuthGrantToken:
    query = session.query(OAuthGrantToken).options(
        # noload(User.api_keys)
    ).filter_by(code=code)
    if lock_update:
        query = query.with_for_update()

    token = query.first()
    if token is None:
        return None
        # raise NotFoundException("User not found")
    return token


@sql_session
def save_grant_token(
        client_id: UUID,
        user_id: UUID,
        code: str,
        redirect_uri: str,
        scopes: List[str],
        session: Session
) -> bool:
    scopes = " ".join(scopes)
    token = OAuthGrantToken(
        client_id=client_id,
        user_id=user_id,
        code=code,
        id=uuid.uuid4(),
        redirect_uri=redirect_uri,
        scope=scopes,
        expires=datetime.utcnow() + timedelta(seconds=100)
    )
    try:
        session.add(token)
        session.commit()
    except Exception:
        return False
    return True


@sql_session
def delete_grant_token_by_code(code: str, session: Session):
    delete_grant_token(get_grant_token_by_code(code, session), session)


@sql_session
def delete_grant_token(token: OAuthGrantToken, session: Session):
    session.delete(token)


@sql_session
def bearer_token_exists_by_id(grant_id: UUID, session: Session) -> bool:
    return session.query(OAuthBearerToken).filter_by(id=grant_id).count() != 0


@sql_session
def get_bearer_token_by_id(grant_id: UUID, session: Session, lock_update: bool = False) -> OAuthBearerToken:
    query = session.query(OAuthBearerToken).options(
        # noload(User.api_keys)
    ).filter_by(id=grant_id)
    if lock_update:
        query = query.with_for_update()

    token = query.first()
    if token is None:
        return None
        # raise NotFoundException("User not found")
    return token


@sql_session
def get_bearer_token_by_refresh_token(token: str, session: Session, lock_update: bool = False) -> OAuthBearerToken:
    query = session.query(OAuthBearerToken).options(
        # noload(User.api_keys)
    ).filter_by(refresh_token=token)
    if lock_update:
        query = query.with_for_update()

    token = query.first()
    if token is None:
        return None
        # raise NotFoundException("User not found")
    return token


@sql_session
def save_bearer_token(
        client_id: UUID,
        user_id: UUID,
        access_token: str,
        refresh_token: str,
        scopes: List[str],
        expires_in: int,
        session: Session
) -> bool:
    scopes = " ".join(scopes)
    expires = datetime.utcnow() + timedelta(seconds=expires_in)
    token = OAuthBearerToken(
        id=uuid.uuid4(),
        client_id=client_id,
        user_id=user_id,
        access_token=access_token,
        refresh_token=refresh_token,
        scope=scopes,
        expires=expires
    )
    try:
        session.add(token)
        session.commit()
    except Exception:
        return False
    return True
