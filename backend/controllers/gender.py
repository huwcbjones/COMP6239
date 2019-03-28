from backend.controller import Controller
from backend.models import UserGender


class GenderController(Controller):
    route = [r"/gender"]

    async def get(self):
        self.write({g.value: g.name.replace("_", " ").capitalize() for g in UserGender})
