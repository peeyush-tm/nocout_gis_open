from django.db import models


class Command(models.Model):
    """
    Model Command Columns declared.
    """
    name = models.CharField(max_length=100, unique=True)
    alias = models.CharField(max_length=100)
    command_line = models.CharField(max_length=100)

    def __unicode__(self):
        """
        Command Objects representation

        """
        return self.name
    