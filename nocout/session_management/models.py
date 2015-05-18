"""
===================================================================================
Module contains database models and functions specific to 'session_management' app.
===================================================================================

Location:
* /nocout_gis/nocout/session_management/models.py

List of constructs:
=======
Classes
=======
* Visitor
* AuthToken

=========
Functions
=========
* session_handler
"""

import os
import binascii
from django.db import models
from django.db.models.signals import pre_delete
from django.contrib.sessions.models import Session
from django.conf import settings
import logging

logger = logging.getLogger(__name__)


class Visitor(models.Model):
    """
    Model for storing logged in user's/visitor's session key.
    Used for tracking logged in user's/visitor's.
    """
    user = models.OneToOneField(settings.AUTH_USER_MODEL, null=False)
    session_key = models.CharField(null=False, max_length=40)


def session_handler(sender, **kwargs):
    """
    A signal call to delete session key from the visitor table.
    """
    Visitor.objects.filter(session_key=kwargs.get('instance').session_key).delete()


class AuthToken(models.Model):
    """
    Model for storing the default authorization tokens.
    """
    key = models.CharField(max_length=40, primary_key=True)
    user = models.OneToOneField(settings.AUTH_USER_MODEL, related_name='auth_token')
    updated = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        """
        Before storing object to database convert key to it's hexadecimal representation.
        """
        self.key = self.generate_key()

        return super(AuthToken, self).save(*args, **kwargs)

    def generate_key(self):
        """
        Return the hexadecimal representation of the binary data.
        Every byte of data is converted into the corresponding 2-digit hex representation.
        The resulting string is therefore twice as long as the length of data.
        """
        return binascii.hexlify(os.urandom(20)).decode()

    def __unicode__(self):
        return self.key


# ****************************** SESSION HANDLING SIGNALS ********************************

# Delete session key from 'Visitor' model before deleting user session.
pre_delete.connect(session_handler, sender=Session)