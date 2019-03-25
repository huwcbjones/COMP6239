import logging
import unittest
import uuid

from backend.database import Database
from backend.models import User, OAuthClient, OAuthGrantType, OAuthResponseType
from backend.models.oauth import save_bearer_token, get_bearer_token_by_access_token, get_bearer_token_by_refresh_token
from backend.utils import random_string


class OAuthBearerTokenTest(unittest.TestCase):

    @classmethod
    def setUpClass(cls) -> None:
        logging.getLogger().setLevel(logging.DEBUG)
        Database(
            "localhost",
            5432,
            "postgres",
            "comp6239",
            sql_echo=True
        )
        cls.db = Database.instance
        cls.db.set_wrap_sessions(True)

    def setUp(self):
        self.db.recreate_db()
        self.s = self.db.session()

    def tearDown(self) -> None:
        self.s.close()

    def test_token(self):
        u = User(
            id=uuid.uuid4(),
            first_name="Test",
            last_name="User",
            email="test@example.com"
        )

        c = OAuthClient(
            id=uuid.uuid4(),
            user_id=u.id,
            grant_type=OAuthGrantType.PASSWORD,
            response_type=OAuthResponseType.AUTHORIZATION_CODE,
            _scopes="*",
            _redirect_uris="http://localhost:8080/oauth/authorize"
        )

        self.s.add(u)
        self.s.add(c)
        self.s.commit()

        access_token = random_string(32)
        refresh_token = random_string(32)
        save_bearer_token(
            client_id=c.id,
            user_id=u.id,
            access_token=access_token,
            refresh_token=refresh_token,
            expires_in=3600,
            scopes=["*"]
        )

        t = get_bearer_token_by_access_token(access_token)
        self.assertIsNotNone(t)

        t = get_bearer_token_by_refresh_token(refresh_token)
        self.assertIsNotNone(t)
