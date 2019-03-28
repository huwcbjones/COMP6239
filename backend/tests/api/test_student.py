import logging
from http import HTTPStatus

from backend.models import UserRole
from backend.tests.api import APITestCase

log = logging.getLogger(__name__)
logging.getLogger().setLevel(logging.DEBUG)


class TestStudentRegister(APITestCase):

    def test_register(self):
        with self.post("/register", json={
            "first_name": "Test",
            "last_name": "User",
            "email": "test@" + self.test_time,
            "password": "Test1!",
            "gender": "n",
            "role": UserRole.STUDENT.value,
            "location": "TestServer"
        }) as r:
            self.assertEqual(r.status_code, HTTPStatus.CREATED, r.json())

        self.setUpOAuthClient("test@" + self.test_time, "Test1!")

        with self.delete("/student/profile", json={"password": "Test1!"}) as r:
            self.assertEqual(r.status_code, HTTPStatus.NO_CONTENT)
