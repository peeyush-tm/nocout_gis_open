import datetime

from django.db import models


class UserAction(models.Model):
    """
    User log models to store the user actions.
    """
    user_id = models.IntegerField()
    action = models.TextField()
    module = models.CharField(max_length=128)
    logged_at = models.DateTimeField(auto_now_add=True)
