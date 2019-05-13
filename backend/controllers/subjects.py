from http import HTTPStatus

from sqlalchemy.orm import Session

from backend.controller import Controller
from backend.database import generate_unique_id
from backend.exc import UnauthorisedException, ResourceAlreadyExistsException, NotFoundException
from backend.models import UserRole, Subject
from backend.models.subject import get_subjects, subject_exists_by_name, subject_exists_by_id, get_subject_by_id
from backend.oauth import protected
from backend.utils.regex import uuid as uuid_regex


class AllSubjectsController(Controller):
    route = [
        r"/subject"
    ]

    async def get(self):
        subjects = get_subjects()
        self.write([{"id": s.id, "name": s.name} for s in subjects])

    @protected
    async def put(self):
        if self.current_user.role != UserRole.ADMIN:
            raise UnauthorisedException()

        permissible_fields = [
            "name",
        ]
        self.check_required_fields(*permissible_fields)

        with self.app.db.session() as s:
            subject_name = self.json_args["name"]  # type: str
            if subject_exists_by_name(subject_name, s):
                raise ResourceAlreadyExistsException("A subject with that name already exists")
            subject = Subject(
                id=generate_unique_id(subject_exists_by_id, s),
                name=subject_name.capitalize()
            )
            s.add(subject)
            s.commit()
            self.write({"id": subject.id, "name": subject.name})


class SubjectController(Controller):
    route = [
        r"/subject/(" + uuid_regex + ")"
    ]

    @protected
    async def delete(self, subject_id):
        if self.current_user.role != UserRole.ADMIN:
            raise UnauthorisedException()

        with self.app.db.session() as s:  # type: Session
            if not subject_exists_by_id(subject_id, s):
                raise NotFoundException("A subject with that ID was not found")
            subject = get_subject_by_id(subject_id, s)
            s.delete(subject)
            s.commit()

            self.set_status(HTTPStatus.NO_CONTENT)
