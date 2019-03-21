from sqlalchemy.orm import Session

from backend.controller import Controller
from backend.exc import UnauthorisedException
from backend.models.user import get_user_by_email

failed_login = UnauthorisedException("Email and/or password are incorrect")


class LoginController(Controller):
    route = [r"/login"]

    async def post(self):
        self.check_required_fields(
            "email",
            "password"
        )
        with self.app.db.session() as s:  # type: Session
            user = get_user_by_email(self.json_args["email"], s)
            if user is None:
                raise failed_login
            if not user.verify_password(self.json_args["password"]):
                raise failed_login
            self.write({"message": "Logged in"})
