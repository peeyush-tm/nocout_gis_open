"""
Permissions Required Mixin to be used for class based views through-out the system.
SuperUser Required Mixin to be used for class based views through-out the system.

References :

    - http://www.robgolding.com/blog/2012/07/12/django-class-based-view-mixins-part-1/
    - https://django-braces.readthedocs.org/en/latest/
"""

from django.core.exceptions import PermissionDenied
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from user_profile.utils.auth import in_group


class PermissionsRequiredMixin(object):
    """
    View mixin which verifies that the logged in user has the specified
    permissions.

    Settings:

    `required_permissions` - list/tuple of required permissions

    Example Usage:

        class SomeView(PermissionsRequiredMixin, ListView):
            ...
            required_permissions = (
                'app1.permission_a',
                'app2.permission_b',
            )
            ...
    """
    required_permissions = ()

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        has_perm = True
        try:
            if request.user.is_superuser:
                return super(PermissionsRequiredMixin, self).dispatch(request, *args, **kwargs)
                
            if type(self.required_permissions) != type(str()):
                perm_codename = self.required_permissions[0].split('.')[1]
            else:
                perm_codename = self.required_permissions.split('.')[1]

            has_permission = in_group(user=request.user, perm_codename=perm_codename)

            if has_permission:
                return super(PermissionsRequiredMixin, self).dispatch(request, *args, **kwargs)
            else:
                has_perm = False
                # if not request.user.has_perms(self.required_permissions):
                #     has_perm = False
                #     raise PermissionDenied
                raise PermissionDenied
        except Exception, e:
            if not has_perm:
                raise PermissionDenied
            pass

        return super(PermissionsRequiredMixin, self).dispatch(request, *args, **kwargs)


class SuperUserRequiredMixin(object):
    """
    View mixin which requires that the authenticated user is a super user
    (i.e. `is_superuser` is True).
    """

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_superuser:
            raise PermissionDenied
        return super(SuperUserRequiredMixin, self).dispatch(request, *args, **kwargs)

