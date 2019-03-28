import logging
from http import HTTPStatus

from backend.models import UserRole, UserGender
from backend.tests.api import APITestCase

log = logging.getLogger(__name__)
logging.getLogger().setLevel(logging.DEBUG)


class TestStudentRegister(APITestCase):

    def test_register(self):
        data = {}
        with self.post("/register", json=data) as r:
            self.assertEqual(r.status_code, HTTPStatus.BAD_REQUEST, r.json())

        data["first_name"] = "Test"
        with self.post("/register", json=data) as r:
            self.assertEqual(r.status_code, HTTPStatus.BAD_REQUEST, r.json())

        data["last_name"] = "User"
        with self.post("/register", json=data) as r:
            self.assertEqual(r.status_code, HTTPStatus.BAD_REQUEST, r.json())

        data["email"] = "test@" + self.test_time
        with self.post("/register", json=data) as r:
            self.assertEqual(r.status_code, HTTPStatus.BAD_REQUEST, r.json())

        data["password"] = "Test1!"
        with self.post("/register", json=data) as r:
            self.assertEqual(r.status_code, HTTPStatus.BAD_REQUEST, r.json())

        data["role"] = UserRole.STUDENT.value
        with self.post("/register", json=data) as r:
            self.assertEqual(r.status_code, HTTPStatus.BAD_REQUEST, r.json())

        data["location"] = "Test Server"
        with self.post("/register", json=data) as r:
            self.assertEqual(r.status_code, HTTPStatus.CREATED, r.json())
            self.assertTrue("gender" in r.json(), "Gender not found")
            self.assertTrue(r.json()["gender"] == UserGender.PREFER_NOT_TO_SAY.value)

        self.setUpOAuthClient(data["email"], data["password"])

        with self.delete("/student/profile", json={"password": data["password"]}) as r:
            self.assertEqual(HTTPStatus.NO_CONTENT, r.status_code)

    def test_profile_edit(self):
        data = {
            "email": "test@" + self.test_time,
            "password": "Test1!",
            "first_name": "Test",
            "last_name": "User",
            "role": UserRole.STUDENT.value,
            "location": "Test Server",
        }

        with self.post("/register", json=data) as r:
            self.assertEqual(r.status_code, HTTPStatus.CREATED, r.json())

        self.setUpOAuthClient(data["email"], data["password"])

        profile_id = None
        with self.get("/student/profile") as r:
            self.assertEqual(r.status_code, HTTPStatus.OK, r.json())
            j = r.json()
            profile_id = j["id"]
            del j["subjects"]
            del j["id"]
            expected = data.copy()
            del expected["password"]
            expected["gender"] = UserGender.PREFER_NOT_TO_SAY.value
            self.assertDictEqual(expected, j)

        edit_data = {
            "email": "test-user@" + self.test_time,
            "password": "failed",
            "first_name": "User",
            "last_name": "Test",
            "gender": UserGender.MALE.value,
            "role": UserRole.TUTOR.value,
            "location": "Testing",
            "subjects": [],
            "id": profile_id
        }
        with self.post("/student/profile", json=edit_data) as r:
            self.assertEqual(r.status_code, HTTPStatus.OK, r.json())
            j = r.json()
            expected = edit_data.copy()
            del expected["password"]
            expected["role"] = UserRole.STUDENT.value

            self.assertDictEqual(expected, j)

        with self.delete("/student/profile", json={"password": edit_data["password"]}) as r:
            self.assertEqual(r.status_code, HTTPStatus.BAD_REQUEST)

        with self.delete("/student/profile", json={"password": data["password"]}) as r:
            self.assertEqual(r.status_code, HTTPStatus.NO_CONTENT)

    def test_subjects(self):
        data = {
            "email": "test@" + self.test_time,
            "password": "Test1!",
            "first_name": "Test",
            "last_name": "User",
            "role": UserRole.STUDENT.value,
            "location": "Test Server",
        }

        with self.post("/register", json=data) as r:
            self.assertEqual(r.status_code, HTTPStatus.CREATED, r.json())

        self.setUpOAuthClient(data["email"], data["password"])

        with self.get("/subject") as r:
            subjects = r.json()
        if not subjects:
            return

        subject = subjects[0]
        with self.post("/student/profile/subject", json=[subject["id"]]) as r:
            self.assertEqual(HTTPStatus.OK, r.status_code, r.json())

        with self.get("/student/profile") as r:
            self.assertEqual([subject], r.json()["subjects"])

        with self.delete("/student/profile/subject", json=[subject["id"]]) as r:
            self.assertEqual(HTTPStatus.OK, r.status_code, r.json())

        with self.get("/student/profile") as r:
            self.assertEqual([], r.json()["subjects"])

        with self.delete("/student/profile", json={"password": data["password"]}) as r:
            self.assertEqual(r.status_code, HTTPStatus.NO_CONTENT)
