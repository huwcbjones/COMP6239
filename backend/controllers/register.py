from http import HTTPStatus

from sqlalchemy.orm import Session

from backend.controller import Controller
from backend.database import generate_unique_id
from backend.exc import ResourceAlreadyExistsException, BadRequestException
from backend.models import User, UserRole, UserGender, TutorProfile
from backend.models.user import user_exists_by_email, user_exists_by_id


class RegisterController(Controller):
    route = [r"/register"]

    async def post(self):
        permissible_fields = [
            "email",
            "first_name",
            "last_name",
            "location",
            "role",
            "password"
        ]
        required_fields = permissible_fields.copy()
        required_fields.append("gender")

        self.check_required_fields(*permissible_fields)
        if not UserRole.contains(self.json_args["role"]):
            valid_roles = list(UserRole.values())
            valid_roles.remove("a")
            raise BadRequestException("Invalid role provided: must be in: {}".format(
                ", ".join(valid_roles)
            ))
        else:
            self.json_args["role"] = UserRole(self.json_args["role"])

        if "gender" not in self.json_args or not UserGender.contains(self.json_args["gender"]):
            self.json_args["gender"] = UserGender.PREFER_NOT_TO_SAY
        else:
            self.json_args["gender"] = UserGender(self.json_args["gender"])

        with self.app.db.session() as s:
            if user_exists_by_email(self.json_args["email"], s):
                raise ResourceAlreadyExistsException("An account with that email already exists")
            new_user = User(**self.get_valid_fields(*required_fields))
            new_user.id = generate_unique_id(user_exists_by_id, s)
            s.add(new_user)
            if new_user.role == UserRole.TUTOR:
                await self.create_blank_tutor_profile(new_user, s)
            s.commit()
            self.set_status(HTTPStatus.CREATED)
            self.write({
                "id": new_user.id,
                "first_name": new_user.first_name,
                "last_name": new_user.last_name,
                "email": new_user.email,
                "gender": new_user.gender,
                "role": new_user.role,
                "location": new_user.location
            })

    async def create_blank_tutor_profile(self, tutor: User, session: Session):
        with session:
            profile = TutorProfile()
            profile.tutor_id = tutor.id
            session.add(profile)
