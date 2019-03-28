import re
from typing import Optional
from uuid import UUID

from backend.controller import Controller
from backend.exc import NotFoundException, BadRequestException
from backend.models import UserRole, UserGender
from backend.models.subject import get_subject_by_id
from backend.models.user import get_student_by_id, get_subjects_by_student_id, user_exists_by_id
from backend.oauth import protected
from backend.utils.regex import uuid as uuid_regex

_uuid_regex = re.compile(uuid_regex)


class StudentProfileController(Controller):
    route = [
        r"/student/profile",
        r"/student/(" + uuid_regex + ")/profile"
    ]

    @protected
    async def get(self, student_id: Optional[UUID] = None):
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
    async def post(self, student_id: Optional[UUID] = None):
        permissible_fields = [
            "email",
            "first_name",
            "last_name",
            "gender",
            "location"
        ]

        if student_id is not None:
            raise BadRequestException()

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


class StudentSubjectProfileController(Controller):
    route = [
        r"/student/profile/subject",
        r"/student/(" + uuid_regex + ")/profile/subject"
    ]

    @protected
    async def get(self, student_id: Optional[UUID] = None):
        if student_id is None:
            student_id = self.current_user.id
        if not user_exists_by_id(student_id):
            raise NotFoundException("Student with that ID not found")
        subjects = get_subjects_by_student_id(student_id)
        self.write(subjects)

    @protected
    async def post(self, student_id: Optional[UUID] = None):
        if student_id is not None:
            raise BadRequestException()

        if not isinstance(self.json_args, list):
            raise BadRequestException("Invalid body")

        with self.app.db.session() as s:
            student = get_student_by_id(self.current_user.id, session=s)

            if not self.json_args:
                self.write(student.subjects)
                return

            subject_ids = [UUID(s_id) for s_id in self.json_args if _uuid_regex.match(s_id)]
            for s_id in subject_ids:
                subject = get_subject_by_id(s_id, session=s)
                if subject is None:
                    continue
                student.subjects.append(subject)
            s.merge(student)
            s.commit()
            self.write(student.subjects)

    @protected
    async def delete(self, student_id: Optional[UUID] = None):
        if student_id is not None:
            raise BadRequestException()

        if not isinstance(self.json_args, list):
            raise BadRequestException("Invalid body")

        with self.app.db.session() as s:
            student = get_student_by_id(self.current_user.id, session=s)

            if not self.json_args:
                self.write(student.subjects)
                return

            subject_ids = [UUID(s_id) for s_id in self.json_args if _uuid_regex.match(s_id)]
            for s_id in subject_ids:
                subject = get_subject_by_id(s_id, session=s)
                if subject is None:
                    continue
                if subject in student.subjects:
                    student.subjects.remove(subject)
            s.merge(student)
            s.commit()
            self.write(student.subjects)
