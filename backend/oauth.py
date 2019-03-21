import logging
import os
import uuid

from oauthlib.oauth2 import RequestValidator, Server
from sqlalchemy.orm import Session

from backend.database import Database
from backend.models.oauth import client_exists_by_id, get_client_by_id, get_grant_token_by_code, \
    get_bearer_token_by_refresh_token, delete_grant_token_by_code, save_grant_token, save_bearer_token
from backend.models.user import get_user_by_email, user_exists_by_email

log = logging.getLogger(__name__)


class AppRequestValidator(RequestValidator):

    def _get_client_credentials_from_request(self, request):
        """Return client credentials based on the current request.
                According to the rfc6749, client MAY use the HTTP Basic authentication
                scheme as defined in [RFC2617] to authenticate with the authorization
                server. The client identifier is encoded using the
                "application/x-www-form-urlencoded" encoding algorithm per Appendix B,
                and the encoded value is used as the username; the client password is
                encoded using the same algorithm and used as the password. The
                authorization server MUST support the HTTP Basic authentication scheme
                for authenticating clients that were issued a client password.
                See `Section 2.3.1`_.
                .. _`Section 2.3.1`: https://tools.ietf.org/html/rfc6749#section-2.3.1
                """
        if request.client_id is not None:
            return request.client_id, request.client_secret

        auth = request.headers.get('Authorization')
        # If Werkzeug successfully parsed the Authorization header,
        # `extract_params` helper will replace the header with a parsed dict,
        # otherwise, there is nothing useful in the header and we just skip it.
        if isinstance(auth, dict):
            return auth['username'], auth['password']

        return None, None

    def authenticate_client(self, request, *args, **kwargs):
        """Authenticate itself in other means.
        Other means means is described in `Section 3.2.1`_.
        .. _`Section 3.2.1`: http://tools.ietf.org/html/rfc6749#section-3.2.1
        """
        client_id, client_secret = self._get_client_credentials_from_request(request)
        log.debug('Authenticating client %r', client_id)

        client = get_client_by_id(client_id)
        if not client:
            log.debug('Authenticating client failed, client not found.')
            return False

        request.client = client

        # http://tools.ietf.org/html/rfc6749#section-2
        # The client MAY omit the parameter if the client secret is an empty string.
        if hasattr(client, 'client_secret') and not client.verify_client_secret(client_secret):
            log.debug('Authenticating client failed, secret not match.')
            return False

        log.debug('Authenticating client succeeded.')
        return True

    def authenticate_client_id(self, client_id, request, *args, **kwargs):
        """Authenticate a non-confidential client.
        :param client_id: Client ID of the non-confidential client
        :param request: The Request object passed by oauthlib
        """
        if client_id is None:
            client_id, _ = self._get_client_credentials_from_request(request)

        log.debug('Authenticating client %r.', client_id)
        client = request.client or get_client_by_id(client_id)

        if not client:
            log.debug('Authenticating client failed, client not found.')
            return False

        # attach client on request for convenience
        request.client = client
        return True

    def confirm_redirect_uri(self, client_id, code, redirect_uri, client,
                             *args, **kwargs):
        """Ensure client is authorized to redirect to the redirect_uri.
        This method is used in the authorization code grant flow. It will
        compare redirect_uri and the one in grant token strictly, you can
        add a `validate_redirect_uri` function on grant for a customized
        validation.
        """
        client = client or get_client_by_id(client_id)
        log.debug('Confirm redirect uri for client %r and code %r.',
                  client.client_id, code)
        grant = get_grant_token_by_code(code)
        if not grant:
            log.debug('Grant not found.')
            return False
        if hasattr(grant, 'validate_redirect_uri'):
            return grant.validate_redirect_uri(redirect_uri)
        log.debug('Compare redirect uri for grant %r and %r.',
                  grant.redirect_uri, redirect_uri)

        testing = 'OAUTHLIB_INSECURE_TRANSPORT' in os.environ
        if testing and redirect_uri is None:
            # For testing
            return True

        return grant.redirect_uri == redirect_uri

    def get_original_scopes(self, refresh_token, request, *args, **kwargs):
        """Get the list of scopes associated with the refresh token.
        This method is used in the refresh token grant flow.  We return
        the scope of the token to be refreshed so it can be applied to the
        new access token.
        """
        log.debug('Obtaining scope of refreshed token.')
        tok = get_bearer_token_by_refresh_token(refresh_token)
        return tok.scopes

    def confirm_scopes(self, refresh_token, scopes, request, *args, **kwargs):
        """Ensures the requested scope matches the scope originally granted
        by the resource owner. If the scope is omitted it is treated as equal
        to the scope originally granted by the resource owner.
        DEPRECATION NOTE: This method will cease to be used in oauthlib>0.4.2,
        future versions of ``oauthlib`` use the validator method
        ``get_original_scopes`` to determine the scope of the refreshed token.
        """
        if not scopes:
            log.debug('Scope omitted for refresh token %r', refresh_token)
            return True
        log.debug('Confirm scopes %r for refresh token %r',
                  scopes, refresh_token)
        tok = get_bearer_token_by_refresh_token(refresh_token=refresh_token)
        return set(tok.scopes) == set(scopes)

    def get_default_redirect_uri(self, client_id, request, *args, **kwargs):
        """Default redirect_uri for the given client."""
        request.client = request.client or get_client_by_id(client_id)
        redirect_uri = request.client.default_redirect_uri
        log.debug('Found default redirect uri %r', redirect_uri)
        return redirect_uri

    def get_default_scopes(self, client_id, request, *args, **kwargs):
        """Default scopes for the given client."""
        request.client = request.client or get_client_by_id(client_id)
        scopes = request.client.default_scopes
        log.debug('Found default scopes %r', scopes)
        return scopes

    def invalidate_authorization_code(self, client_id, code, request,
                                      *args, **kwargs):
        """Invalidate an authorization code after use.
        We keep the temporary code in a grant, which has a `delete`
        function to destroy itself.
        """
        log.debug('Destroy grant token for client %r, %r', client_id, code)
        delete_grant_token_by_code(code)

    def save_authorization_code(self, client_id, code, request,
                                *args, **kwargs):
        """Persist the authorization code."""
        log.debug(
            'Persist authorization code %r for client %r',
            code, client_id
        )
        request.client = request.client or get_client_by_id(client_id)
        save_grant_token(
            client_id,
            uuid.uuid4(),
            code=code,
            redirect_uri=request.redirect_uri,
            scopes=request.scopes
        )
        return request.client.default_redirect_uri

    def save_bearer_token(self, token, request, *args, **kwargs):
        """Persist the Bearer token."""
        log.debug('Save bearer token %r', token)
        save_bearer_token(
            request.client_id,
            request.user.id,
            token["access_token"],
            token["refresh_token"],
            token["scope"],
            token["expires_in"]
        )
        return request.client.default_redirect_uri

    def validate_client_id(self, client_id, request, *args, **kwargs):
        with Database.instance.session() as s:  # type: Session
            return client_exists_by_id(client_id, s)

    def validate_grant_type(self, client_id, grant_type, client, request,
                            *args, **kwargs):
        """Ensure the client is authorized to use the grant type requested.
        It will allow any of the four grant types (`authorization_code`,
        `password`, `client_credentials`, `refresh_token`) by default.
        Implemented `allowed_grant_types` for client object to authorize
        the request.
        It is suggested that `allowed_grant_types` should contain at least
        `authorization_code` and `refresh_token`.
        """
        default_grant_types = (
            'authorization_code', 'password',
            'client_credentials', 'refresh_token',
        )

        # Grant type is allowed if it is part of the 'allowed_grant_types'
        # of the selected client or if it is one of the default grant types
        if hasattr(client, 'allowed_grant_types'):
            if grant_type not in client.allowed_grant_types:
                return False
        else:
            if grant_type not in default_grant_types:
                return False

        if grant_type == 'client_credentials':
            if not hasattr(client, 'user'):
                log.debug('Client should have a user property')
                return False
            request.user = client.user
        return True

    def validate_redirect_uri(self, client_id, redirect_uri, request, *args, **kwargs):
        request.client = request.client or get_client_by_id(client_id)
        client = request.client
        if hasattr(client, 'validate_redirect_uri'):
            return client.validate_redirect_uri(redirect_uri)
        return redirect_uri in client.redirect_uris

    def validate_refresh_token(self, refresh_token, client, request,
                               *args, **kwargs):
        """Ensure the token is valid and belongs to the client
        This method is used by the authorization code grant indirectly by
        issuing refresh tokens, resource owner password credentials grant
        (also indirectly) and the refresh token grant.
        """

        token = get_bearer_token_by_refresh_token(refresh_token)

        if token and token.client_id == client.client_id:
            # Make sure the request object contains user and client_id
            request.client_id = token.client_id
            request.user = token.user
            return True
        return False

    def validate_response_type(self, client_id, response_type, client, request,
                               *args, **kwargs):
        """Ensure client is authorized to use the response type requested.
        It will allow any of the two (`code`, `token`) response types by
        default. Implemented `allowed_response_types` for client object
        to authorize the request.
        """
        if response_type not in ('code', 'token'):
            return False

        if hasattr(client, 'allowed_response_types'):
            return response_type in client.allowed_response_types
        return True

    def validate_scopes(self, client_id, scopes, client, request, *args, **kwargs):
        if hasattr(client, 'validate_scopes'):
            return client.validate_scopes(scopes)
        return set(client.default_scopes).issuperset(set(scopes))

    def validate_user(self, username, password, client, request, *args, **kwargs):
        if not user_exists_by_email(username):
            return False
        user = get_user_by_email(username)
        if user.verify_password(password):
            request.user = user
            return True
        return False


validator = AppRequestValidator()
server = Server(validator)
