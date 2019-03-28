from uuid import UUID

from backend.controller import Controller
from backend.exc import NotFoundException
from backend.models import UserRole
from backend.models.user import get_user_by_id
from backend.oauth import protected
from backend.utils.regex import uuid as uuid_regex


class TutorProfileController(Controller):
    route = [
        r"/tutor/profile",
        r"/tutor/(" + uuid_regex + ")/profile"
    ]

    @protected
    async def get(self, tutor_id: UUID = None):
        if tutor_id is None:
            tutor_id = self.current_user.id
        tutor = get_user_by_id(tutor_id)
        if tutor is None or tutor.role != UserRole.TUTOR:
            raise NotFoundException("Tutor not found!")

        data = {
            "id": tutor.id,
            "first_name": tutor.first_name,
            "last_name": tutor.last_name
        }
        if tutor.id == self.current_user.id:
            data["email"] = tutor.email
        self.write(data)
