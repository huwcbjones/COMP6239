import uuid

from backend.controller import Controller
from backend.database import sql_session
from backend.exc import ResourceAlreadyExistsException, BadRequestException
from backend.models import User, UserRole, UserGender
from backend.models.user import user_exists_by_email, user_exists_by_id


class RegisterController(Controller):
    route = [r"/register"]

    async def post(self):
        self.check_required_fields(
            "email",
            "first_name",
            "last_name",
            "gender",
            "location",
            "role",
            "password"
        )
        if UserRole.contains(self.json_args["role"]):
            valid_roles = list(UserRole.values())
            valid_roles.remove("a")
            raise BadRequestException("Invalid role provided: must be in: {}".format(
                ", ".join(valid_roles)
            ))

        if not UserGender.contains(self.json_args["gender"]):
            raise BadRequestException("Invalid gender provided: must be in: {}".format(
                ", ".join(UserGender.values())
            ))

        with self.app.db.session() as s:
            if user_exists_by_email(self.json_args["email"], s):
                raise ResourceAlreadyExistsException("An account with that email already exists")
            self.json_args["role"] = UserRole(self.json_args["role"])
            new_user = User(**self.json_args)
            new_user.id = self._generate_unique_id(s)
            s.add(new_user)
            s.commit()
            self.write({"msg": "registered"})

    @sql_session
    def _generate_unique_id(self, session):
        while True:
            id = uuid.uuid4()
            if not user_exists_by_id(id, session):
                return id
