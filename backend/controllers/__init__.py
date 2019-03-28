import glob
from os.path import dirname, basename, isfile

from backend.controller import Controller, WebSocketController

modules = glob.glob(dirname(__file__)+"/*.py")
__all__ = [ basename(f)[:-3] for f in modules if isfile(f) and not f.endswith('__init__.py')]

from . import *


class PingController(Controller):

    route = [r"/ping"]
    async def get(self):
        self.write({"message": "Pong!"})
