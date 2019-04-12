import datetime
import uuid
from typing import List, Optional

from bcrypt import hashpw, gensalt, checkpw
from sqlalchemy import Column, String, LargeBinary, ForeignKey, Enum, DateTime, Table, Integer, Numeric, func, inspect
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import relationship
from sqlalchemy_utils import UUIDType, EmailType

from backend.utils import enum
from backend.utils.hash import hash_string, compare_hash

Base = declarative_base()


class TimestampMixin(object):
    created_at = Column(DateTime, default=func.now())


class TimestampModifiedMixin(TimestampMixin):
    modified_at = Column(DateTime, default=func.now(), onupdate=func.current_timestamp())


# region Enums


class UserRole(enum.Enum):
    ADMIN = "a"
    STUDENT = "s"
    TUTOR = "t"


class UserGender(enum.Enum):
    FEMALE = "f"
    MALE = "m"
    PREFER_NOT_TO_SAY = "n"


class MessageState(enum.Enum):
    SENT = "s"
    DELIVERED = "d"
    READ = "r"


class OAuthGrantType(enum.Enum):
    AUTHORIZATION_CODE = "authorization_code"
    IMPLICIT = "implicit"
    PASSWORD = "password"
    CLIENT_CREDENTIALS = "client_credentials"
    DEVICE_CODE = "device_code"
    REFRESH_TOKEN = "refresh_token"


class OAuthResponseType(enum.Enum):
    AUTHORIZATION_CODE = "code"


# endregion

student_subject_assoc_table = Table(
    'students_subjects',
    Base.metadata,
    Column('subject_id', UUIDType, ForeignKey('subjects.id', ondelete="CASCADE")),
    Column('student_id', UUIDType, ForeignKey('users.id', ondelete="CASCADE"))
)

tutor_subject_assoc_table = Table(
    'tutors_subjects',
    Base.metadata,
    Column('subject_id', UUIDType, ForeignKey('subjects.id', ondelete="CASCADE")),
    Column('profile_id', Integer, ForeignKey('tutor_profiles.id', ondelete="CASCADE"))
)


class Subject(Base):
    __tablename__ = "subjects"

    id = Column(UUIDType, primary_key=True)
    name = Column(String, unique=True)
    students = relationship(
        "Student",
        secondary=student_subject_assoc_table
    )
    tutors = relationship(
        "TutorProfile",
        secondary=tutor_subject_assoc_table
    )


class User(TimestampModifiedMixin, Base):
    __tablename__ = "users"

    id = Column(UUIDType, primary_key=True)
    first_name = Column(String)
    last_name = Column(String)
    email = Column(EmailType, unique=True)
    _password = Column("password", LargeBinary(60))

    role = Column(Enum(UserRole))
    gender = Column(Enum(UserGender))

    location = Column(String)

    @property
    def password(self):
        return self._password

    @password.setter
    def password(self, value):
        self._password = hashpw(value.encode(), gensalt())

    def verify_password(self, password) -> bool:
        return checkpw(password.encode(), self._password)


class Student(User):
    subjects = relationship(
        Subject,
        secondary=student_subject_assoc_table,
        order_by=Subject.name
    )


class TutorProfile(TimestampModifiedMixin, Base):
    __tablename__ = "tutor_profiles"

    id = Column(Integer, autoincrement=True, primary_key=True)
    tutor_id = Column(UUIDType, ForeignKey(User.id, ondelete="CASCADE"), nullable=False)
    tutor = relationship(User, foreign_keys=[tutor_id])

    bio = Column(String)
    reviewed_at = Column(DateTime)

    reason = Column(String)
    reviewed_id = Column(UUIDType, ForeignKey(User.id, ondelete="CASCADE"))
    approved_by = relationship(User, foreign_keys=[reviewed_id])

    price = Column(Numeric())

    subjects = relationship(
        Subject,
        secondary=tutor_subject_assoc_table,
        order_by=Subject.name
    )

    def review(self, user_id: uuid.UUID, reason: str = None):
        self.reason = reason
        self.reviewed_at = datetime.datetime.utcnow()
        self.reviewed_id = user_id

    @hybrid_property
    def state(self) -> Optional[bool]:
        """
        Get the profile state

        * true: profile has been approved
        * false: profile has been denied
        * None: profile is awaiting approval

        :return: Optional[bool]
        """
        if self.reviewed_at is None:
            return None
        return self.reason is None


class Tutor:

    def __init__(self, tutor: User, profile: TutorProfile):
        super().__setattr__("_tutor", tutor)
        super().__setattr__("_profile", profile)
        del self._profile.tutor

    def __getattr__(self, item):
        if hasattr(self, "_tutor") and hasattr(self._tutor, item):
            return getattr(self._tutor, item)
        if hasattr(self, "_profile") and hasattr(self._profile, item):
            return getattr(self._profile, item)
        raise AttributeError()

    def __setattr__(self, key, value):
        if hasattr(self, "_tutor") and hasattr(self._tutor, key):
            return self._tutor.__setattr__(key, value)
        if hasattr(self, "_profile") and hasattr(self._profile, key):
            return self._profile.__setattr__(key, value)
        super().__setattr__(key, value)

    @property
    def user(self) -> User:
        return self._tutor

    @property
    def profile(self) -> TutorProfile:
        return self._profile

    def fields(self, include_private=False):
        profile = self._get_fields(self._profile)
        tutor = self._get_fields(self._tutor)
        fields = {**profile, **tutor}
        self._remove_fields(fields, ["password", "created_at", "tutor", "reviewed_by"])
        if not include_private:
            self._remove_fields(fields, ["reason", "reviewed_at", "reviewed_id", "state", "email"])
        return fields

    def _remove_fields(self, dct, keys):
        [self._remove_field(dct, k) for k in keys]

    def _remove_field(self, dct, key):
        if key in dct:
            del dct[key]

    def _get_fields(self, obj):
        return_fields = {}
        inspection = inspect(obj)
        fields = [field for field in dir(obj) if not field.startswith("_") and field != "metadata"]
        for field in fields:
            if field in inspection.unloaded:
                continue
            data = obj.__getattribute__(field)
            if callable(data):
                continue
            return_fields[field] = data
        return return_fields


class Rating(TimestampModifiedMixin, Base):
    __tablename__ = "tutor_ratings"

    tutor_id = Column(UUIDType, ForeignKey(User.id, ondelete="CASCADE"), primary_key=True)
    student_id = Column(UUIDType, ForeignKey(User.id, ondelete="CASCADE"), primary_key=True)

    subject_id = Column(UUIDType, ForeignKey(Subject.id, ondelete="CASCADE"))
    rating = Column(Integer, nullable=False)
    feedback = Column(String)

    date = Column(DateTime, nullable=False)


class Message(TimestampMixin, Base):
    __tablename__ = "messages"

    id = Column(UUIDType, primary_key=True)  # type: uuid.UUID
    from_id = Column(UUIDType, ForeignKey(User.id, ondelete="CASCADE"))  # type: uuid.UUID
    to_id = Column(UUIDType, ForeignKey(User.id, ondelete="CASCADE"))  # type: uuid.UUID

    message = Column(String)  # type: str
    state = Column(Enum(MessageState))  # type: MessageState


# region OAuth Classes
class OAuthClient(TimestampModifiedMixin, Base):
    __tablename__ = "oauth_clients"

    id = Column(UUIDType, primary_key=True)
    _client_secret = Column(LargeBinary(60), default=None)

    @property
    def client_secret(self):
        return self._client_secret

    @client_secret.setter
    def client_secret(self, value):
        if value is None:
            self._client_secret = None
        else:
            self._client_secret = hashpw(value.encode(), gensalt())

    def verify_client_secret(self, secret) -> bool:
        if secret is not None:
            return checkpw(secret.encode(), self._client_secret)
        if self._client_secret is None:
            return True
        return checkpw(secret.encode(), self._client_secret)

    user_id = Column(UUIDType, ForeignKey(User.id, ondelete="CASCADE"))
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


class OAuthBearerToken(TimestampModifiedMixin, Base):
    __tablename__ = "oauth_bearer_tokens"

    id = Column(UUIDType, primary_key=True)

    _access_token = Column(LargeBinary(64), unique=True)

    @property
    def access_token(self):
        return self._access_token

    @access_token.setter
    def access_token(self, value):
        self._access_token = hash_string(value)

    def verify_access_token(self, token) -> bool:
        return compare_hash(self._access_token, hash_string(token))

    _refresh_token = Column(LargeBinary(64))

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

    client_id = Column(UUIDType, ForeignKey(OAuthClient.id, ondelete="CASCADE"))
    client = relationship(OAuthClient)

    user_id = Column(UUIDType, ForeignKey(User.id, ondelete="CASCADE"))
    user = relationship(User)

    expires = Column(DateTime)

    scope = Column(String)

    @property
    def scopes(self):
        if self.scope:
            return self.scope.split()
        return []


class OAuthGrantToken(TimestampModifiedMixin, Base):
    __tablename__ = "oauth_grant_tokens"

    id = Column(UUIDType, primary_key=True)

    user_id = Column(UUIDType, ForeignKey(User.id, ondelete="CASCADE"))
    user = relationship(User)

    client_id = Column(UUIDType, ForeignKey(OAuthClient.id, ondelete="CASCADE"))
    client = relationship(OAuthClient)

    _code = Column(LargeBinary(64))

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
# endregion
