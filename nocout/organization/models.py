import datetime
from django.db import models


# organization model
from mptt.models import MPTTModel, TreeForeignKey


class Organization(MPTTModel, models.Model):
    """
    Organization Model columns declaration.
    """
    name = models.CharField('Name', max_length=250, unique=True)
    alias = models.CharField('Alias', max_length=250)
    city = models.CharField('City', max_length=200, null=True, blank=True)
    state = models.CharField('State', max_length=200, null=True, blank=True)
    country = models.CharField('Country', max_length=200, null=True, blank=True)
    parent = TreeForeignKey('self', null=True, blank=True, related_name='organization_children')
    description = models.TextField('Description', null=True, blank=True)

    def __str__(self):
        """
        Organization object representation.
        """
        return self.name

