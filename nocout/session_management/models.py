

from django.db import models
try:
    from django.contrib.auth import get_user_model
except ImportError:  # django < 1.5
    from django.contrib.auth.models import User
else:
    User = get_user_model()
from django.db.models.signals import pre_delete
from django.contrib.sessions.models import Session

import logging
logger=logging.getLogger(__name__)


class Visitor(models.Model):
    """
    Vistior Models columns Declaration
    """
    user = models.OneToOneField(User, null=False)
    session_key = models.CharField(null=False, max_length=40)


def session_handler(sender, **kwargs):
    """
    A signal call to delete session key from the visitor table.
    """
    Visitor.objects.filter(session_key = kwargs.get('instance').session_key ).delete()


pre_delete.connect(session_handler, sender=Session)
