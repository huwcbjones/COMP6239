import inspect
import logging
import os
from typing import Callable, Dict, Any, Optional

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session

from backend.models import Base

logger = logging.getLogger(__name__)


class _WrappedSession:
    def __init__(self, session, log_wrap=False):
        self._counter = 0
        self.__log_wrap = log_wrap
        self.__session = session
        self.__session_status("opened")

    def close(self):
        self.__session_status("closed")
        self.__session.close()

    def __session_status(self, session_state):
        if not self.__log_wrap:
            return
        stack = inspect.stack()
        position = None
        parent = None
        for frame in stack:
            if "sql.py" not in frame.filename:
                filename = os.path.abspath(frame.filename)
                if "/python" in filename:
                    filename = filename.split("/python")
                    filename = "PYTHON:/" + "/python".join(filename[1:])
                string = "{}:{}:{}".format(filename, frame.lineno, frame.function)
                if position is None:
                    position = string
                elif parent is None:
                    parent = string
                    break
        logger.debug(
            "Session {} {} in {} (called from {})".format(self.__session.hash_key, session_state, position, parent))

    def __getattr__(self, item):
        return getattr(self.__session, item)

    def __enter__(self):
        self._counter = self._counter + 1
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._counter = self._counter - 1
        if self._counter == 0:
            self.close()


class Database:

    instance = None  # type: Optional[Database]

    def __init__(self, hostname: str, port: int, user: str, password: str, **kwargs):
        """
        Connect to the database
        :param hostname:
        :param user:
        :param password:
        :param kwargs:
        :return:
        """
        self._engine = None
        self._connection = None
        self._session = None
        self._host = hostname
        self._user = user
        self._password = password
        self._port = port
        self._database = "comp6239"
        self._wrap_sessions = False

        for key, value in kwargs.items():
            if hasattr(self, "_" + key) and value is not None:
                setattr(self, "_" + key, value)

        logger.info("Initialising database connection...")
        self.connection_string = self._get_sql_connection_string()
        logger.debug("Connection: {}".format(self.connection_string))

        self._engine = create_engine(
            self.connection_string,
            echo="sql_echo" in kwargs and kwargs["sql_echo"],
            pool_recycle=30,
            max_overflow=2
        )
        self._connection = self._engine.connect()
        self._session = sessionmaker(self._engine)
        self.__class__.instance = self
        logger.info("Database connection established!")

    def recreate_db(self):
        if not self.is_connected():
            return
        Base.metadata.drop_all(self._engine)
        Base.metadata.create_all(self._engine)

    def session(self) -> Session:
        """
        Get a database session
        :return:
        """
        return _WrappedSession(self._session(), self._wrap_sessions)

    def set_wrap_sessions(self, state: bool):
        """
        Set whether database sessions should be wrapped or not
        Wrapping a session enables logging when a session is opened/closed
        :param state:
        :return:
        """
        self._wrap_sessions = state

        # need debug to see session logging
        if state:
            logger.setLevel(logging.DEBUG)
        else:
            logger.setLevel(logging.getLogger().getEffectiveLevel())

    def _get_sql_connection_string(self):
        return "postgresql+psycopg2://{}:{}@{}:{}/{}?client_encoding=utf8".format(
            self._user, self._password, self._host, self._port, self._database
        )

    def is_connected(self):
        if self._engine is None or self._connection is None:
            return False
        return not self._connection.closed


def sql_session(func: Callable) -> Callable:
    def wrapper(*args, **kwargs):
        session_passed_in_kwargs = "session" in kwargs or ("session" in kwargs and kwargs["session"] is not None)
        session_passed_in_args = False
        session = None
        for arg in args:
            if isinstance(arg, (Session, _WrappedSession)):
                session_passed_in_args = True
                session = arg
                break
        if session_passed_in_args:
            args = [i for i in args if i != session]
            kwargs["session"] = session
        elif session_passed_in_kwargs:
            session = kwargs["session"]
        else:
            session = Database.instance.session()
            kwargs["session"] = session
        with session:
            return func(*args, **kwargs)

    return wrapper
