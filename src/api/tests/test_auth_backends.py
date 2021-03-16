from api.auth_backends import JWTAuthentication
from django.test import TestCase
from rest_framework.exceptions import AuthenticationFailed

from api.mocks import MockRequest
from api.models import Profile, AuthUser
from api.utils import tokenutils


class JWTAuthenticationTest(TestCase):
    def setUp(self):

        self.profile = Profile.objects.create(
            first_name="Test", last_name="User", email="test@test.com"
        )
        self.auth_user = AuthUser.objects.create(
            user_id="google-oauth2|123456789", profile=self.profile
        )

    def tearDown(self):
        self.auth_user.delete()
        self.profile.delete()

        self.auth_user = None
        self.profile = None
        self.request = None

    # def test_pass_authenticate(self):
    #     token = tokenutils.create_token(self.auth_user.user_id)
    #     request = MockRequest(token=token)
    #     auth = JWTAuthentication()
    #
    #     user, token = auth.authenticate(request)
    #
    #     assert user.profile.id == self.profile.id
    #     assert token == token

    def test_authenticate_expired_token(self):
        token = tokenutils.create_token(self.auth_user.user_id, expire_in=-1000)
        request = MockRequest(token=token)
        auth = JWTAuthentication()

        with self.assertRaises(AuthenticationFailed):
            _ = auth.authenticate(request)

    def test_authenticate_invalid_token(self):
        request = MockRequest(token="abc123")
        auth = JWTAuthentication()

        user, token = auth.authenticate(request)

        assert user is None
        assert token is None

    def test_authenticate_no_token(self):
        request = MockRequest(token=None)
        auth = JWTAuthentication()

        with self.assertRaises(AuthenticationFailed):
            _ = auth.authenticate(request)
