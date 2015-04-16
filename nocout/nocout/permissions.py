from rest_framework import permissions


class DjangoModelPermissions(permissions.DjangoModelPermissions):
    """
    The request is authenticated using `django.contrib.auth` permissions.
    See: https://docs.djangoproject.com/en/dev/topics/auth/#permissions
    It ensures that the user is authenticated, and has the appropriate
    `add`/`change`/`delete`/`view` permissions on the model.
    This permission can only be applied against view classes that
    provide a `.model` or `.queryset` attribute.
    """

    perms_map = {
        'GET': ['%(app_label)s.view_%(model_name)s'],
        'OPTIONS': [],
        'HEAD': ['%(app_label)s.view_%(model_name)s'],
        'POST': ['%(app_label)s.add_%(model_name)s'],
        'PUT': ['%(app_label)s.change_%(model_name)s'],
        'PATCH': ['%(app_label)s.change_%(model_name)s'],
        'DELETE': ['%(app_label)s.delete_%(model_name)s'],
    }

