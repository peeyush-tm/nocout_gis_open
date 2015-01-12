import binascii
import os

from django.db import models
from django.db.models.signals import pre_delete
from django.contrib.sessions.models import Session

from django.conf import settings

import logging
logger=logging.getLogger(__name__)


class Visitor(models.Model):
    """
    Vistior Models columns Declaration
    """
    user = models.OneToOneField(settings.AUTH_USER_MODEL, null=False)
    session_key = models.CharField(null=False, max_length=40)


def session_handler(sender, **kwargs):
    """
    A signal call to delete session key from the visitor table.
    """
    Visitor.objects.filter(session_key = kwargs.get('instance').session_key ).delete()


pre_delete.connect(session_handler, sender=Session)


class AuthToken(models.Model):
    """
    The default authorization token model.
    """
    key = models.CharField(max_length=40, primary_key=True)
    user = models.OneToOneField(settings.AUTH_USER_MODEL, related_name='auth_token')
    updated = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        self.key = self.generate_key()
        return super(Token, self).save(*args, **kwargs)

    def generate_key(self):
        return binascii.hexlify(os.urandom(20)).decode()

    def __unicode__(self):
        return self.key
