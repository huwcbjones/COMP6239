from backend.controller import Controller
from backend.models import OAuthGrantType, OAuthResponseType
from backend.oauth import server


class OAuthAuthorizeController(Controller):
    route = [r"/oauth/authorize"]

    async def post(self):
        scores = self.request
        pass


class OAuthTokenController(Controller):
    route = [r"/oauth/token"]

    async def post(self):
        credentials = {}

        headers, body, status = server.create_token_response(
            self.request.uri,
            self.request.method,
            self.request.body,
            self.request.headers,
            credentials
        )
        [self.add_header(h, v) for h, v in headers.items()]
        self.set_status(status)
        self.write(body)


class OAuthGrantTypesController(Controller):
    route = [r"/oauth/grant_types"]

    async def get(self):
        self.write({g.value: g.name.replace("_", " ").capitalize() for g in OAuthGrantType})


class OAuthResponseTypesController(Controller):
    route = [r"/oauth/response_types"]

    async def get(self):
        self.write({g.value: g.name.replace("_", " ").capitalize() for g in OAuthResponseType})
