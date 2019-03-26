import re
from uuid import UUID

from backend.controller import Controller
from backend.exc import NotFoundException, BadRequestException
from backend.models import UserRole, UserGender
from backend.models.subject import get_subject_by_id
from backend.models.user import get_user_by_id, get_student_by_id
from backend.oauth import protected
from backend.utils.regex import uuid as uuid_regex


class StudentProfileController(Controller):
    route = [
        r"/student/profile",
        r"/student/(" + uuid_regex + ")/profile"
    ]

    @protected
    async def get(self, student_id: UUID = None):
        if student_id is None:
            student_id = self.current_user.id
        with self.app.db.session() as s:
            student = get_student_by_id(student_id, s)
            if student is None or student.role != UserRole.STUDENT:
                raise NotFoundException("Student not found!")

            data = {
                "id": student.id,
                "first_name": student.first_name,
                "last_name": student.last_name,
                "gender": student.gender,
                "role": student.role,
                "location": student.location,
                "subjects": student.subjects
            }
        if student.id == self.current_user.id:
            data["email"] = student.email
        self.write(data)

    @protected
    async def post(self, student_id: UUID = None):
        permissible_fields = [
            "email",
            "first_name",
            "last_name",
            "gender",
            "location"
        ]

        with self.app.db.session() as s:
            student = get_student_by_id(self.current_user.id, session=s, lock_update=True)
            if student is None or student.role != UserRole.STUDENT:
                raise NotFoundException("Student not found!")

            if not UserGender.contains(self.json_args["gender"]):
                raise BadRequestException("Invalid gender provided: must be in: {}".format(
                    ", ".join(UserGender.values())
                ))
            else:
                self.json_args["gender"] = UserGender(self.json_args["gender"])

            self.merge_fields(student, *permissible_fields)
            if "subjects" in self.json_args:
                student.subjects.clear()
                _uuid_regex = re.compile(uuid_regex)
                subject_ids = [UUID(s_id) for s_id in self.json_args["subjects"] if _uuid_regex.match(s_id)]
                for s_id in subject_ids:
                    subject = get_subject_by_id(s_id)
                    if subject is None:
                        continue
                    student.subjects.append(subject)

            s.add(student)
            s.commit()
            data = {
                "id": student.id,
                "first_name": student.first_name,
                "last_name": student.last_name,
                "email": student.email,
                "gender": student.gender,
                "role": student.role,
                "location": student.location,
                "subjects": student.subjects
            }

        self.write(data)


class TutorProfileController(Controller):
    route = [
        r"/tutor/profile",
        r"/tutor/(" + uuid_regex + ")/profile"
    ]

    @protected
    async def get(self, tutor_id: UUID = None):
        if tutor_id is None:
            tutor_id = self.current_user.id
        tutor = get_user_by_id(tutor_id)
        if tutor is None or tutor.role != UserRole.TUTOR:
            raise NotFoundException("Tutor not found!")

        data = {
            "id": tutor.id,
            "first_name": tutor.first_name,
            "last_name": tutor.last_name
        }
        if tutor.id == self.current_user.id:
            data["email"] = tutor.email
        self.write(data)
