import re
from http import HTTPStatus
from typing import Optional
from uuid import UUID

from backend.controller import Controller
from backend.exc import NotFoundException, BadRequestException, UnauthorisedException
from backend.models import UserRole, UserGender
from backend.models.student import get_student_by_id, get_subjects_by_student_id
from backend.models.subject import get_subject_by_id, get_tutor_threads_by_student_id, \
    get_tutor_request_threads_by_student_id
from backend.models.user import user_exists_by_id, user_is_role
from backend.oauth import protected
from backend.utils.regex import uuid as uuid_regex

_uuid_regex = re.compile(uuid_regex)


class StudentProfileController(Controller):
    route = [
        r"/student/profile",
        r"/student/(" + uuid_regex + ")/profile"
    ]

    @protected
    async def get(self, student_id: Optional[str] = None):
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

    @protected(roles=[UserRole.STUDENT])
    async def post(self, student_id: Optional[str] = None):
        permissible_fields = [
            "email",
            "first_name",
            "last_name",
            "gender",
            "location"
        ]

        if student_id is not None and UUID(student_id) != self.current_user.id:
            raise BadRequestException()

        with self.app.db.session() as s:
            student = get_student_by_id(self.current_user.id, session=s, lock_update=True)
            if student is None:
                raise NotFoundException("Student not found!")

            if self.json_args.get("gender") is not None:
                if not UserGender.contains(self.json_args.get("gender")):
                    raise BadRequestException("Invalid gender provided: must be in: {}".format(
                        ", ".join(UserGender.values())
                    ))
                else:
                    self.json_args["gender"] = UserGender(self.json_args["gender"])

            self.merge_fields(student, *permissible_fields)
            if "subjects" in self.json_args:
                student.subjects.clear()
                subject_ids = [UUID(s["id"]) for s in self.json_args["subjects"] if _uuid_regex.match(s.get("id"))]
                for s_id in subject_ids:
                    subject = get_subject_by_id(s_id, s)
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

    @protected(roles=[UserRole.STUDENT])
    async def delete(self, student_id: Optional[str] = None):
        permissible_fields = [
            "password",
        ]

        if student_id is not None:
            raise BadRequestException()

        with self.app.db.session() as s:
            student = get_student_by_id(self.current_user.id, session=s, lock_update=True)
            if student is None:
                raise NotFoundException("Student not found!")

            if not student.verify_password(self.json_args["password"]):
                raise UnauthorisedException("Invalid password")

            s.delete(student)
            s.commit()

        self.set_status(HTTPStatus.NO_CONTENT)
        self.finish()


class StudentSubjectProfileController(Controller):
    route = [
        r"/student/profile/subject",
        r"/student/(" + uuid_regex + ")/profile/subject"
    ]

    @protected
    async def get(self, student_id: Optional[str] = None):
        if student_id is None:
            student_id = self.current_user.id
        if not user_exists_by_id(student_id):
            raise NotFoundException("Student with that ID not found")
        if not user_is_role(student_id, UserRole.STUDENT):
            raise NotFoundException()
        subjects = get_subjects_by_student_id(student_id)
        self.write(subjects)

    @protected(roles=[UserRole.STUDENT])
    async def post(self, student_id: Optional[str] = None):
        if student_id is not None:
            raise BadRequestException()
        student_id = self.current_user.id

        if not isinstance(self.json_args, list):
            raise BadRequestException("Invalid body")

        with self.app.db.session() as s:
            student = get_student_by_id(student_id, session=s)

            if not self.json_args:
                self.write(student.subjects)
                return

            subject_ids = [UUID(s_id.get("id")) for s_id in self.json_args if _uuid_regex.match(s_id.get("id"))]
            for s_id in subject_ids:
                subject = get_subject_by_id(s_id, session=s)
                if subject is None:
                    continue
                student.subjects.append(subject)
            s.merge(student)
            s.commit()
            self.write(student.subjects)

    @protected(roles=[UserRole.STUDENT])
    async def delete(self, student_id: Optional[str] = None):
        if student_id is not None:
            raise BadRequestException()
        student_id = self.current_user.id

        if not isinstance(self.json_args, list):
            raise BadRequestException("Invalid body")

        with self.app.db.session() as s:
            student = get_student_by_id(student_id, session=s)

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


class Tutors(Controller):
    route = [r"/student/tutors"]

    @protected(roles=[UserRole.STUDENT])
    async def get(self):
        tutees = get_tutor_threads_by_student_id(self.current_user.id)
        self.write([{
            "id": thread.id,
            "recipient": {
                "id": thread.get_recipient(self.current_user.id).id,
                "first_name": thread.get_recipient(self.current_user.id).first_name,
                "last_name": thread.get_recipient(self.current_user.id).last_name
            },
            "message_count": thread.message_count,
            "messages": [],
            "state": thread.state
        } for thread in tutees])


class TutorRequests(Controller):
    route = [r"/student/requests"]

    @protected(roles=[UserRole.STUDENT])
    async def get(self):
        tutees = get_tutor_request_threads_by_student_id(self.current_user.id)
        self.write([{
            "id": thread.id,
            "recipient": {
                "id": thread.get_recipient(self.current_user.id).id,
                "first_name": thread.get_recipient(self.current_user.id).first_name,
                "last_name": thread.get_recipient(self.current_user.id).last_name
            },
            "message_count": thread.message_count,
            "messages": [],
            "state": thread.state
        } for thread in tutees])
