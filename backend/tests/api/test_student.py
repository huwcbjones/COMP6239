from http import HTTPStatus
from typing import List, Dict

from backend.models import UserRole, UserGender
from backend.tests.api import APITestCase


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


class TestStudentEditProfile(APITestCase):

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
            self.assertEqual(r.status_code, HTTPStatus.UNAUTHORIZED)

        with self.delete("/student/profile", json={"password": data["password"]}) as r:
            self.assertEqual(r.status_code, HTTPStatus.NO_CONTENT)


class TestStudentSubjectEdit(APITestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.register_tutor()
        cls.setUpOAuthClient()
        with cls.get("/subject") as r:
            cls.subjects = r.json()  # type: List[Dict[str, str]]

    @classmethod
    def tearDownClass(cls) -> None:
        with cls.delete("/student/profile", json={"password": cls.password}) as r:
            assert r.status_code == HTTPStatus.NO_CONTENT

        super().tearDownClass()

    @classmethod
    def register_tutor(cls):
        cls.email = "student@" + cls.test_time
        cls.password = "Test1!"
        data = {
            "email": cls.email,
            "password": cls.password,
            "role": UserRole.STUDENT.value,
            "location": "test server",
            "first_name": "Test",
            "last_name": "Student"
        }
        with cls.post("/register", json=data) as r:
            assert r.status_code == HTTPStatus.CREATED
            cls.user_id = r.json()["id"]

    def test_add_subject(self):
        with self.get("/student/profile/subject") as r:
            self.assertEqual(r.status_code, HTTPStatus.OK, r.json())
            self.assertEqual([], r.json())

        subjects = []
        for s in self.subjects:
            subjects.append(s)
            with self.post("/student/profile/subject", json=[s["id"]]) as r:
                self.assertEqual(r.status_code, HTTPStatus.OK, r.json())
                self.assertEqual(subjects, r.json())

    def test_delete_subject(self):
        with self.post("/student/profile/subject", json=[s["id"] for s in self.subjects]) as r:
            self.assertEqual(r.status_code, HTTPStatus.OK, r.json())
            self.assertEqual(self.subjects, r.json())

        subjects = self.subjects.copy()
        for s in self.subjects:
            subjects.remove(s)
            with self.delete("/student/profile/subject", json=[s["id"]]) as r:
                self.assertEqual(r.status_code, HTTPStatus.OK, r.json())
                self.assertEqual(subjects, r.json())
