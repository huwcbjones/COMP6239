from uuid import UUID

from backend.controller import Controller
from backend.exc import NotFoundException
from backend.models import UserRole
from backend.models.user import get_user_by_id
from backend.oauth import protected
from backend.utils.regex import uuid as uuid_regex


class StudentProfileController(Controller):
    route = [
        r"/student/profile",
        r"/student/(" + uuid_regex + ")/profile"
    ]

    @protected
    async def get(self, student_id: UUID = None):
        if student_id is None:
            student_id = self.current_user.id
        student = get_user_by_id(student_id)
        if student is None or student.role != UserRole.STUDENT:
            raise NotFoundException("Student not found!")

        data = {
            "id": student.id,
            "first_name": student.first_name,
            "last_name": student.last_name
        }
        if student.id == self.current_user.id:
            data["email"] = student.email
        self.write(data)
