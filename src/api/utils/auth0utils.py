import logging
import random
import string

from django.utils.encoding import smart_text
from django.utils.translation import ugettext as _
from jose import jws, jwt
from rest_framework import exceptions
from rest_framework.authentication import get_authorization_header

from api.models import Application, AuthUser
from app import settings
from auth0.v3.authentication import GetToken
from auth0.v3.management import Auth0

logger = logging.getLogger(__name__)


class Auth0ClientManager(object):
    _chars = string.ascii_letters + string.digits
    _secret_len = 48

    def __init__(self, domain, token):
        self.domain = domain
        self.token = token
        self.auth0 = Auth0(domain, token)

    def delete_client(self, client_id):
        self.auth0.clients.delete(client_id)

    def get_client(self, client_id):
        return self.auth0.clients.get(client_id)

    def list_clients(self):
        return self.auth0.clients.all()

    def change_secret(self, client_id):
        c = [random.choice(self._chars) for x in range(self._secret_len)]
        secret = "".join(c)
        body = {"client_secret": secret}
        return self.auth0.clients.update(client_id, body)

    def create_non_interactive_client(self, name, description=None, callbacks=[]):
        params = {
            "name": name,
            "app_type": "non_interactive",
            "description": description or "",
            "token_endpoint_auth_method": "client_secret_basic",
            "callbacks": callbacks,
        }
        resp = self.auth0.clients.create(params)

        return resp

    def create_client_grant(self, client_id, audience, scopes):
        params = {
            "client_id": client_id,
            "audience": audience,
            "scope": scopes,
        }
        resp = self.auth0.client_grants.create(params)

        return resp


class Auth0UserInfo(object):

    user_url = "/api/v2/users/{id}"

    def __init__(self, domain, token):
        self.domain = domain
        self.token = token
        self.auth0 = Auth0(domain, token)

    def get_userinfo(self, user_id):
        return self.auth0.users.get(user_id)


class Auth0ManagementAPI(object):
    def __init__(self, domain, client_id, client_secret):
        self.domain = domain
        self.client_id = client_id
        self.client_secret = client_secret

    def get_token(self):
        audience = settings.ADMIN_API_AUDIENCE
        _get_token = GetToken(self.domain)
        token = _get_token.client_credentials(
            self.client_id, self.client_secret, audience
        )
        return token["access_token"]


def is_hs_token(token):

    try:
        jwt.decode(
            token,
            settings.API_SIGNING_SECRET,
            options={
                "verify_signature": False,
                "verify_aud": False,
                "verify_iat": False,
                "verify_exp": False,
                "verify_nbf": False,
                "verify_iss": False,
                "verify_sub": False,
                "verify_jti": False,
            },
        )
        return True
    except jwt.JWTError:
        return False


def get_jwt_token(request):
    token = None
    auth = get_authorization_header(request).split()

    if len(auth) == 2:
        auth_header_prefix = "Bearer"

        if not auth:
            return None

        if smart_text(auth[0].lower()) != auth_header_prefix.lower():
            return None

        token = auth[1]
    elif len(auth) > 2:
        msg = _(
            "Invalid Authorization header. Credentials string "
            "should not contain spaces."
        )
        raise exceptions.AuthenticationFailed(msg)
    else:
        token = request.query_params.get("access_token")

    if token is None:
        msg = _("Invalid Authorization header. No credentials provided.")
        raise exceptions.AuthenticationFailed(msg)

    return token


def get_user_info(user_id):
    domain = settings.AUTH0_DOMAIN
    client_id = settings.ADMIN_API_CLIENT_ID
    client_secret = settings.ADMIN_API_CLIENT_SECRET

    auth = Auth0ManagementAPI(domain, client_id, client_secret)
    token = auth.get_token()
    auth_user = Auth0UserInfo(domain, token)
    ui = auth_user.get_userinfo(user_id)
    um = ui.get("user_metadata") or {}
    return dict(
        first_name=um.get("first_name") or ui.get("given_name") or "",
        last_name=um.get("last_name") or ui.get("family_name") or "",
        email=um.get("email") or ui["email"],
    )


def get_token_algorithm(token):
    unverified_header = jws.get_unverified_header(token)
    return unverified_header.get("alg")


def decode_hs(token):
    try:
        return jwt.decode(
            token,
            settings.API_SIGNING_SECRET,
            audience=settings.API_AUDIENCE,
            algorithms=["HS256"],
        )
    except jwt.JWTError as e:
        logger.debug("Decode token failed: {}".format(str(e)))
        raise exceptions.AuthenticationFailed(e)


def decode(token):
    alg = get_token_algorithm(token)
    if alg == "HS256":
        return decode_hs(token)

    msg = "{} algorithm not supported".format(alg)
    raise exceptions.ValidationError(msg, code=400)


def get_unverified_profile(token):
    payload = jwt.get_unverified_claims(token)
    return _get_profile(payload)


def get_profile(token):
    payload = decode(token)
    return _get_profile(payload)


def _get_profile(payload):
    sub = payload.get("sub")
    if not sub:
        return None

    if "@clients" in sub:
        client_id = sub.split("@clients")[0]
        try:
            app = Application.objects.get(client_id=client_id)
            return app.profile
        except Application.DoesNotExist:
            return None
    elif "|" in sub:
        try:
            auth_user = AuthUser.objects.get(user_id=sub)
            return auth_user.profile
        except AuthUser.DoesNotExist:
            return None

    return None
