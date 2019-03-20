import enum
from typing import List

from bcrypt import hashpw, gensalt, checkpw
from sqlalchemy import Column, String, Binary, ForeignKey, Enum, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy_utils import UUIDType, EmailType

Base = declarative_base()


class UserRole(enum.Enum):
    ADMIN = "a"
    STUDENT = "s"
    TUTOR = "t"


class OAuthGrantType(enum.Enum):
    AUTHORIZATION_CODE = "authorization_code"
    IMPLICIT = "implicit"
    PASSWORD = "password"
    CLIENT_CREDENTIALS = "client_credentials"
    DEVICE_CODE = "device_code"
    REFRESH_TOKEN = "refresh_token"


class OAuthResponseType(enum.Enum):
    AUTHORIZATION_CODE = "code"


class User(Base):
    __tablename__ = "users"

    id = Column(UUIDType, primary_key=True)
    first_name = Column(String)
    last_name = Column(String)
    email = Column(EmailType, unique=True)
    _password = Column("password", Binary(60))

    role = Column(Enum(UserRole))

    @property
    def password(self):
        return self._password

    @password.setter
    def password(self, value):
        self._password = hashpw(value.encode(), gensalt())

    def verify_password(self, password) -> bool:
        return checkpw(password.encode(), self._password)


class OAuthClient(Base):
    __tablename__ = "oauth_clients"

    id = Column(UUIDType, primary_key=True)
    user = Column(UUIDType, ForeignKey(User.id))  # type: User
    grant_type = Column(Enum(OAuthGrantType))
    response_type = Column(Enum(OAuthResponseType))
    _scopes = Column(String)
    _redirect_uris = Column(String)

    @property
    def redirect_uris(self) -> List[str]:
        if self._redirect_uris:
            return self._redirect_uris.split()
        return []

    @property
    def default_redirect_uri(self):
        return self.redirect_uris[0]

    @property
    def scopes(self):
        if self._scopes:
            return self._scopes.split()
        return []


class OAuthBearerToken(Base):
    __tablename__ = "oauth_bearer_tokens"

    id = Column(UUIDType, primary_key=True)

    access_token = Column(String)
    refresh_token = Column(String)

    client_id = Column(UUIDType, ForeignKey(OAuthClient.id))
    client = relationship(OAuthClient)

    user_id = Column(UUIDType, ForeignKey(User.id))
    user = relationship(User)

    expires = Column(DateTime)

    _scopes = Column(String)

    @property
    def scopes(self):
        if self._scopes:
            return self._scopes.split()
        return []


class OAuthAuthorizationCode(Base):
    __tablename__ = "oauth_authorization_tokens"

    id = Column(UUIDType, primary_key=True)

    user_id = Column(UUIDType, ForeignKey(User.id))
    user = relationship(User)

    client_id = Column(UUIDType, ForeignKey(OAuthClient.id))
    client = relationship(OAuthClient)

    code = Column(String)

    redirect_uri = Column(String)
    expires = Column(DateTime)

    _scopes = Column(String)

    @property
    def scopes(self):
        if self._scopes:
            return self._scopes.split()
        return []

    challenge = Column(String)
    challenge_method = Column(String)
