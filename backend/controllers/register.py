from backend.controller import Controller
from backend.database import generate_unique_id
from backend.exc import ResourceAlreadyExistsException, BadRequestException
from backend.models import User, UserRole, UserGender
from backend.models.user import user_exists_by_email, user_exists_by_id


class RegisterController(Controller):
    route = [r"/register"]

    async def post(self):
        permissible_fields = [
            "email",
            "first_name",
            "last_name",
            "gender",
            "location",
            "role",
            "password"
        ]
        self.check_required_fields(*permissible_fields)
        if not UserRole.contains(self.json_args["role"]):
            valid_roles = list(UserRole.values())
            valid_roles.remove("a")
            raise BadRequestException("Invalid role provided: must be in: {}".format(
                ", ".join(valid_roles)
            ))
        else:
            self.json_args["role"] = UserRole(self.json_args["role"])

        if not UserGender.contains(self.json_args["gender"]):
            raise BadRequestException("Invalid gender provided: must be in: {}".format(
                ", ".join(UserGender.values())
            ))
        else:
            self.json_args["gender"] = UserGender(self.json_args["gender"])

        with self.app.db.session() as s:
            if user_exists_by_email(self.json_args["email"], s):
                raise ResourceAlreadyExistsException("An account with that email already exists")
            new_user = User(**self.get_valid_fields(*permissible_fields))
            new_user.id = generate_unique_id(user_exists_by_id, s)
            s.add(new_user)
            s.commit()
            self.write({"msg": "registered"})
