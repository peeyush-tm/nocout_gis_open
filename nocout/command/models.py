"""
=============================================================================
Module contains database models and functions specific to 'command' app.
=============================================================================

Location:
* /nocout_gis/nocout/command/models.py

List of constructs:
=======
Classes
=======
* Command
"""

from django.db import models


class Command(models.Model):
    """
    Model for storing command instances.
    """
    name = models.CharField(max_length=100, unique=True)
    alias = models.CharField(max_length=100)
    command_line = models.CharField(max_length=100)

    def __unicode__(self):
        return self.name
    