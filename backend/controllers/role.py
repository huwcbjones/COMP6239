from backend.controller import Controller
from backend.models import UserRole


class RoleController(Controller):
    route = [r"/role"]

    async def get(self):
        self.write({r.value: r.name.replace("_", " ").capitalize() for r in UserRole if r != UserRole.ADMIN})
