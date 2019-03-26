from backend.controller import Controller
from backend.database import generate_unique_id
from backend.exc import UnauthorisedException, ResourceAlreadyExistsException
from backend.models import UserRole, Subject
from backend.models.subject import get_subjects, subject_exists_by_name, subject_exists_by_id
from backend.oauth import protected


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
