from uuid import UUID

from backend.controller import Controller
from backend.exc import NotFoundException
from backend.models import UserRole
from backend.models.tutor import get_unapproved_tutors, get_profile_by_tutor_id
from backend.oauth import protected
from backend.utils import str_to_bool
from backend.utils.regex import uuid as uuid_regex


class TutorsRequestsController(Controller):
    route = [r"/admin/tutor"]

    @protected(roles=[UserRole.ADMIN])
    async def get(self):
        tutors = get_unapproved_tutors()
        self.write([t.fields() for t in tutors])


class TutorApprovalController(Controller):
    route = [r"/admin/tutor/(" + uuid_regex + ")"]

    @protected(roles=[UserRole.ADMIN])
    async def post(self, tutor_id: UUID):
        permissible_fields = [
            "status"
        ]
        self.check_required_fields(*permissible_fields)

        approved = str_to_bool(self.json_args["status"])
        reason = self.json_args.get("reason", None)
        if not approved:
            permissible_fields.append("reason")
            self.check_required_fields(*permissible_fields)

        with self.app.db.session() as s:
            tutor = get_profile_by_tutor_id(tutor_id, s)
            if tutor is None:
                raise NotFoundException("Tutor not found!")

            tutor.review(self.current_user.id, reason)

            s.add(tutor)
            s.commit()
