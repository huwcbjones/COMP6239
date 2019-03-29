import logging
from http import HTTPStatus
from typing import List, Dict

from backend.models import UserRole, UserGender
from backend.tests.api import APITestCase

log = logging.getLogger(__name__)
logging.getLogger().setLevel(logging.DEBUG)


class TestTutorRegister(APITestCase):

    def test_register(self):
        data = {}
        with self.post("/register", json=data) as r:
            self.assertEqual(r.status_code, HTTPStatus.BAD_REQUEST, r.json())

        data["first_name"] = "Test"
        with self.post("/register", json=data) as r:
            self.assertEqual(r.status_code, HTTPStatus.BAD_REQUEST, r.json())

        data["last_name"] = "Tutor"
        with self.post("/register", json=data) as r:
            self.assertEqual(r.status_code, HTTPStatus.BAD_REQUEST, r.json())

        data["email"] = "tutor@" + self.test_time
        with self.post("/register", json=data) as r:
            self.assertEqual(r.status_code, HTTPStatus.BAD_REQUEST, r.json())

        data["password"] = "Test1!"
        with self.post("/register", json=data) as r:
            self.assertEqual(r.status_code, HTTPStatus.BAD_REQUEST, r.json())

        data["role"] = UserRole.TUTOR.value
        with self.post("/register", json=data) as r:
            self.assertEqual(r.status_code, HTTPStatus.BAD_REQUEST, r.json())

        data["location"] = "Test Server"
        with self.post("/register", json=data) as r:
            self.assertEqual(r.status_code, HTTPStatus.CREATED, r.json())
            self.assertTrue("gender" in r.json(), "Gender not found")
            self.assertTrue(r.json()["gender"] == UserGender.PREFER_NOT_TO_SAY.value)

        self.setUpOAuthClient(data["email"], data["password"])

        with self.delete("/tutor/profile", json={"password": data["password"]}) as r:
            self.assertEqual(HTTPStatus.NO_CONTENT, r.status_code)


class TestTutorProfileEdit(APITestCase):
    def test_profile_edit(self):
        data = {
            "approved_at": None,
            "bio": None,
            "email": "tutor@" + self.test_time,
            "password": "Test1!",
            "first_name": "Test",
            "last_name": "Tutor",
            "price": None,
            "role": UserRole.TUTOR.value,
            "location": "Test Server"
        }

        with self.post("/register", json=data) as r:
            self.assertEqual(r.status_code, HTTPStatus.CREATED, r.json())
            profile_id = r.json()["id"]

        self.setUpOAuthClient(data["email"], data["password"])

        with self.get("/tutor/profile") as r:
            self.assertEqual(r.status_code, HTTPStatus.OK, r.json())
            j = r.json()
            profile_id = j["id"]
            del j["revision"]
            del j["subjects"]
            del j["id"]
            expected = data.copy()
            del expected["password"]
            expected["gender"] = UserGender.PREFER_NOT_TO_SAY.value
            self.assertDictEqual(expected, j)

        edit_data = {
            "approved_at": None,
            "bio": "Test Bio",
            "email": "test-tutor@" + self.test_time,
            "password": "failed",
            "first_name": "Tutor",
            "last_name": "Test",
            "gender": UserGender.MALE.value,
            "role": UserRole.ADMIN.value,
            "location": "Testing",
            "subjects": [],
            "id": profile_id,
            "price": 15.0,
        }
        with self.post("/tutor/profile", json=edit_data) as r:
            self.assertEqual(r.status_code, HTTPStatus.OK, r.json())
            j = r.json()
            expected = edit_data.copy()
            del expected["password"]
            del j["revision"]
            expected["role"] = UserRole.TUTOR.value

            self.assertDictEqual(expected, j)

        with self.delete("/tutor/profile", json={"password": edit_data["password"]}) as r:
            self.assertEqual(r.status_code, HTTPStatus.BAD_REQUEST)

        with self.delete("/tutor/profile", json={"password": data["password"]}) as r:
            self.assertEqual(r.status_code, HTTPStatus.NO_CONTENT)


class TestTutorSubjectEdit(APITestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.register_tutor()
        cls.setUpOAuthClient()
        with cls.get("/subject") as r:
            cls.subjects = r.json()  # type: List[Dict[str, str]]

    @classmethod
    def tearDownClass(cls) -> None:
        with cls.delete("/tutor/profile", json={"password": cls.password}) as r:
            assert r.status_code == HTTPStatus.NO_CONTENT

        super().tearDownClass()

    @classmethod
    def register_tutor(cls):
        cls.email = "tutor@" + cls.test_time
        cls.password = "Test1!"
        data = {
            "email": cls.email,
            "password": cls.password,
            "role": UserRole.TUTOR.value,
            "location": "test server",
            "first_name": "Test",
            "last_name": "Tutor"
        }
        with cls.post("/register", json=data) as r:
            assert r.status_code == HTTPStatus.CREATED
            cls.user_id = r.json()["id"]

    def test_add_subject(self):
        with self.get("/tutor/profile/subject") as r:
            self.assertEqual(r.status_code, HTTPStatus.OK, r.json())
            self.assertEqual([], r.json())

        subjects = []
        for s in self.subjects:
            subjects.append(s)
            with self.post("/tutor/profile/subject", json=[s["id"]]) as r:
                self.assertEqual(r.status_code, HTTPStatus.OK, r.json())
                self.assertEqual(subjects, r.json())

    def test_delete_subject(self):
        with self.post("/tutor/profile/subject", json=[s["id"] for s in self.subjects]) as r:
            self.assertEqual(r.status_code, HTTPStatus.OK, r.json())
            self.assertEqual(self.subjects, r.json())

        subjects = self.subjects.copy()
        for s in self.subjects:
            subjects.remove(s)
            with self.delete("/tutor/profile/subject", json=[s["id"]]) as r:
                self.assertEqual(r.status_code, HTTPStatus.OK, r.json())
                self.assertEqual(subjects, r.json())
