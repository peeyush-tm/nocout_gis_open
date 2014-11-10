from organization.models import Organization


def logged_in_user_organizations(self_object):
    """
    If the user role is admin then append its descendants organization as well, otherwise not

    :params self_object:
    :return organization_list:
    """
    if self_object.request.user.is_superuser:
        return Organization.objects.all()

    logged_in_user = self_object.request.user.userprofile

    if logged_in_user.role.values_list('role_name', flat=True)[0] == 'admin':
        organizations = logged_in_user.organization.get_descendants(include_self=True)
    else:
        organizations = Organization.objects.filter(id=logged_in_user.organization.id)

    return organizations
