from backend.controller import Controller
from backend.oauth import protected2


class ProfileController(Controller):
    route = [r"/profile"]

    @protected2
    async def get(self):
        self.write({"msg": "hello"})
