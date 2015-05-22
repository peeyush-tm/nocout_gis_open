"""
==============================================================
Module contains backends specific to 'session_management' app.
==============================================================

Description:
    Authenticate user using session_management.models.AuthToken

Location:
* /nocout_gis/nocout/session_management/backends.py

List of constructs:
=======
Classes
=======
* TokenAuthBackend
"""

from django.contrib.auth.backends import ModelBackend
from session_management.models import AuthToken


class TokenAuthBackend(ModelBackend):
    """
    Authenticates against AuthToken.
    If authentication token exist in 'AuthToken' model then return the user else return None.
    """
    def authenticate(self, token=None):
        if token is None:
            return None

        try:
            auth_token = AuthToken.objects.get(key=token)
            return auth_token.user
        except AuthToken.DoesNotExist as e:
            return None
