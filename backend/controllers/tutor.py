import re
from http import HTTPStatus
from typing import Optional
from uuid import UUID

from backend.controller import Controller
from backend.exc import NotFoundException, BadRequestException
from backend.models import UserRole, UserGender
from backend.models.subject import get_subject_by_id
from backend.models.tutor import get_tutors, get_tutor_by_id
from backend.models.user import user_exists_by_id, user_is_role, get_user_by_id
from backend.oauth import protected
from backend.utils.regex import uuid as uuid_regex

_uuid_regex = re.compile(uuid_regex)


class TutorsController(Controller):
    route = [r"/tutor"]

    async def get(self):
        tutors = get_tutors()
        self.write([t.fields() for t in tutors])


class TutorProfileController(Controller):
    route = [
        r"/tutor/profile",
        r"/tutor/(" + uuid_regex + ")/profile"
    ]

    @protected
    async def get(self, tutor_id: Optional[UUID] = None):
        if tutor_id is None and self.current_user.role == UserRole.TUTOR:
            tutor_id = self.current_user.id
        with self.app.db.session() as s:
            tutor = get_tutor_by_id(tutor_id, s, is_approved=self.current_user.role == UserRole.STUDENT)
            if tutor is None or tutor.role != UserRole.TUTOR:
                raise NotFoundException("Tutor not found!")

            data = {
                "id": tutor.id,
                "first_name": tutor.first_name,
                "last_name": tutor.last_name,
                "gender": tutor.gender,
                "role": tutor.role,
                "location": tutor.location,
                "subjects": tutor.subjects,
                "bio": tutor.bio,
                "price": tutor.price
            }
        if tutor.id == self.current_user.id:
            data["email"] = tutor.email
            data["approved_at"] = tutor.approved_at
            data["revision"] = tutor.profile.modified_at
        if self.current_user.role == UserRole.ADMIN:
            data["email"] = tutor.email
            data["approved_at"] = tutor.approved_at
            data["revision"] = tutor.profile.modified_at
            data["approved_by"] = tutor.approved_id
        elif not tutor.is_approved:
            raise NotFoundException("Tutor not found!")
        self.write(data)

    @protected
    async def post(self, tutor_id: Optional[UUID] = None):
        permissible_fields = [
            "email",
            "first_name",
            "last_name",
            "gender",
            "location"
        ]

        if tutor_id is not None:
            raise BadRequestException()

        with self.app.db.session() as s:
            tutor = get_tutor_by_id(self.current_user.id, session=s, lock_update=True)
            if tutor is None or tutor.role != UserRole.STUDENT:
                raise NotFoundException("Student not found!")

            if not UserGender.contains(self.json_args["gender"]):
                raise BadRequestException("Invalid gender provided: must be in: {}".format(
                    ", ".join(UserGender.values())
                ))
            else:
                self.json_args["gender"] = UserGender(self.json_args["gender"])

            self.merge_fields(tutor, *permissible_fields)
            if "subjects" in self.json_args:
                tutor.subjects.clear()
                subject_ids = [UUID(s_id) for s_id in self.json_args["subjects"] if _uuid_regex.match(s_id)]
                for s_id in subject_ids:
                    subject = get_subject_by_id(s_id)
                    if subject is None:
                        continue
                    tutor.subjects.append(subject)

            s.add(tutor)
            s.commit()
            data = {
                "id": tutor.id,
                "first_name": tutor.first_name,
                "last_name": tutor.last_name,
                "email": tutor.email,
                "gender": tutor.gender,
                "role": tutor.role,
                "location": tutor.location,
                "subjects": tutor.subjects
            }

        self.write(data)

    @protected
    async def delete(self, student_id: Optional[UUID] = None):
        permissible_fields = [
            "password",
        ]

        if student_id is not None:
            raise BadRequestException()

        with self.app.db.session() as s:
            tutor = get_user_by_id(self.current_user.id, session=s, lock_update=True)
            if tutor is None or tutor.role != UserRole.TUTOR:
                raise NotFoundException("Tutor not found!")

            if not tutor.verify_password(self.json_args["password"]):
                raise BadRequestException("Invalid password")

            s.delete(tutor)
            s.commit()

        self.set_status(HTTPStatus.NO_CONTENT)
        self.finish()


class TutorSubjectProfileController(Controller):
    route = [
        r"/tutor/profile/subject",
        r"/tutor/(" + uuid_regex + ")/profile/subject"
    ]

    @protected
    async def get(self, tutor_id: Optional[UUID] = None):
        if tutor_id is None:
            tutor_id = self.current_user.id
        if not user_exists_by_id(tutor_id):
            raise NotFoundException("Tutor with that ID not found")
        if not user_is_role(tutor_id, UserRole.TUTOR):
            raise NotFoundException("Tutor with that ID not found")
        subjects = get_subjects_by_tutor_id(tutor_id)
        self.write(subjects)

    @protected
    async def post(self, tutor_id: Optional[UUID] = None):
        if tutor_id is not None:
            raise BadRequestException()
        tutor_id = self.current_user.id

        if not isinstance(self.json_args, list):
            raise BadRequestException("Invalid body")

        if not user_is_role(tutor_id, UserRole.STUDENT):
            raise NotFoundException("Tutor with that ID not found")

        with self.app.db.session() as s:
            tutor = get_tutor_by_id(tutor_id, session=s)

            if not self.json_args:
                self.write(tutor.subjects)
                return

            subject_ids = [UUID(s_id) for s_id in self.json_args if _uuid_regex.match(s_id)]
            for s_id in subject_ids:
                subject = get_subject_by_id(s_id, session=s)
                if subject is None:
                    continue
                tutor.subjects.append(subject)
            s.merge(tutor)
            s.commit()
            self.write(tutor.subjects)

    @protected
    async def delete(self, tutor_id: Optional[UUID] = None):
        if tutor_id is not None:
            raise BadRequestException()
        tutor_id = self.current_user.id

        if not isinstance(self.json_args, list):
            raise BadRequestException("Invalid body")

        if not user_is_role(tutor_id, UserRole.TUTOR):
            raise NotFoundException("Tutor with that ID not found")

        with self.app.db.session() as s:
            tutor = get_tutor_by_id(tutor_id, session=s)

            if not self.json_args:
                self.write(tutor.subjects)
                return

            subject_ids = [UUID(s_id) for s_id in self.json_args if _uuid_regex.match(s_id)]
            for s_id in subject_ids:
                subject = get_subject_by_id(s_id, session=s)
                if subject is None:
                    continue
                if subject in tutor.subjects:
                    tutor.subjects.remove(subject)
            s.merge(tutor)
            s.commit()
            self.write(tutor.subjects)
