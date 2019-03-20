from oauthlib.oauth2 import RequestValidator

class AppRequestValidator(RequestValidator):

    def validate_client_id(self, client_id, request, *args, **kwargs):
        pass
        # try:
