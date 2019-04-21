from backend.controller import Controller
from backend.exc import NotFoundException
from backend.models.user import get_user_by_id
from backend.oauth import protected


class ProfileController(Controller):

    route = [r"/profile"]

    @protected
    async def get(self):
        user_id = self.current_user.id
        with self.app.db.session() as s:
            user = get_user_by_id(user_id, s)
            if user is None:
                raise NotFoundException("Profile not found!")

            data = {
                "id": user.id,
                "email": user.email,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "gender": user.gender,
                "role": user.role,
                "location": user.location
            }
        self.write(data)
