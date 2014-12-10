"""
This module creates view permission for all apps.
"""

from django.db.models.signals import post_syncdb
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.models import Permission


def add_view_permissions(sender, **kwargs):
    """
    This syncdb hooks takes care of adding a view permission too all our
    content types.
    """

    for content_type in ContentType.objects.all():
        codename = "view_%s" % content_type.model
        if not Permission.objects.filter(content_type=content_type, codename=codename):
            Permission.objects.create(content_type=content_type, codename=codename, name="Can view %s" % content_type.name)
            print("Added view permission for %s" % content_type.name)


post_syncdb.connect(add_view_permissions)
