import uuid

from backend.controller import Controller
from backend.database import sql_session
from backend.exc import ResourceAlreadyExistsException, BadRequestException
from backend.models import User, UserRole
from backend.models.user import get_user_by_email, user_exists_by_email, user_exists_by_id


class RegisterController(Controller):

    route = [r"/register"]

    async def post(self):
        self.check_required_fields(
            "email",
            "first_name",
            "last_name",
            "role",
            "password"
        )
        if self.json_args["role"] not in ("s", "t"):
            raise BadRequestException("Invalid role provided: must be either 's' or 't'")
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
            if not user_exists_by_id(id):
                return id
