"""
Authenticate user using session_management.models.AuthToken
"""

from django.contrib.auth.backends import ModelBackend

from session_management.models import AuthToken


class TokenAuthBackend(ModelBackend):
    """
    Authenticates against AuthToken.
    """

    def authenticate(self, token=None):
        if token is None:
            return None

        try:
            auth_token = AuthToken.objects.get(key=token)
            return auth_token.user
        except AuthToken.DoesNotExist as e:
            return None
