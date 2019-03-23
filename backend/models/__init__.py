import enum
import uuid
from typing import List

from bcrypt import hashpw, gensalt, checkpw
from sqlalchemy import Column, String, Binary, ForeignKey, Enum, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy_utils import UUIDType, EmailType

from backend.utils.hash import hash_string, compare_hash

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
    _client_secret = Column(Binary(60), default=None)

    @property
    def client_secret(self):
        return self._client_secret

    @client_secret.setter
    def client_secret(self, value):
        self._client_secret = hashpw(value.encode(), gensalt())

    def verify_client_secret(self, secret) -> bool:
        if secret is not None:
            return checkpw(secret.encode(), self._client_secret)
        if self._client_secret is None:
            return True
        return checkpw(secret.encode(), self._client_secret)

    user_id = Column(UUIDType, ForeignKey(User.id))
    user = relationship(User)

    grant_type = Column(Enum(OAuthGrantType))
    response_type = Column(Enum(OAuthResponseType))
    _scopes = Column(String)
    _redirect_uris = Column(String)

    @property
    def client_id(self) -> uuid.UUID:
        return self.id

    @property
    def redirect_uris(self) -> List[str]:
        if self._redirect_uris:
            return self._redirect_uris.split()
        return []

    @property
    def default_redirect_uri(self):
        return self.redirect_uris[0]

    @property
    def default_scopes(self):
        return self._scopes

    @property
    def scopes(self):
        if self._scopes:
            return self._scopes.split()
        return []


class OAuthBearerToken(Base):
    __tablename__ = "oauth_bearer_tokens"

    id = Column(UUIDType, primary_key=True)

    _access_token = Column(Binary(64), unique=True)

    @property
    def access_token(self):
        return self._access_token

    @access_token.setter
    def access_token(self, value):
        self._access_token = hash_string(value)

    def verify_access_token(self, token) -> bool:
        return compare_hash(self._access_token, hash_string(token))

    _refresh_token = Column(Binary(64))

    @property
    def refresh_token(self):
        return self._refresh_token

    @refresh_token.setter
    def refresh_token(self, value):
        if value is None:
            self._refresh_token = None
        else:
            self._refresh_token = hash_string(value)

    def verify_refresh_token(self, token) -> bool:
        return compare_hash(self._access_token, hash_string(token))

    client_id = Column(UUIDType, ForeignKey(OAuthClient.id))
    client = relationship(OAuthClient)

    user_id = Column(UUIDType, ForeignKey(User.id))
    user = relationship(User)

    expires = Column(DateTime)

    scope = Column(String)

    @property
    def scopes(self):
        if self.scope:
            return self.scope.split()
        return []


class OAuthGrantToken(Base):
    __tablename__ = "oauth_grant_tokens"

    id = Column(UUIDType, primary_key=True)

    user_id = Column(UUIDType, ForeignKey(User.id))
    user = relationship(User)

    client_id = Column(UUIDType, ForeignKey(OAuthClient.id))
    client = relationship(OAuthClient)

    _code = Column(Binary(64))

    @property
    def code(self):
        return self._code

    @code.setter
    def code(self, value):
        self._code = hash_string(value.encode())

    def verify_code(self, code) -> bool:
        return compare_hash(self._code, hash_string(code))

    redirect_uri = Column(String)
    expires = Column(DateTime)

    scope = Column(String)

    @property
    def scopes(self):
        if self.scope:
            return self.scope.split()
        return []

    challenge = Column(String)
    challenge_method = Column(String)
