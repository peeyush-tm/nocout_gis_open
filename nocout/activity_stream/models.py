"""
================================================================================
Module contains database models and functions specific to 'activity_stream' app.
================================================================================

Location:
* /nocout_gis/nocout/activity_stream/models.py

List of constructs:
=======
Classes
=======
* UserAction
"""

from django.db import models


class UserAction(models.Model):
    """
    User log models for storing the user actions.
    """
    user_id = models.IntegerField()
    action = models.TextField()
    module = models.CharField(max_length=128)
    logged_at = models.DateTimeField(auto_now_add=True)
