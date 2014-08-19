


def logged_in_user_organizations(self_object):
    """
    If the user role is admin then append its descendants organization as well, otherwise not

    :params self_object:
    :return organization_list:
    """
    logged_in_user= self_object.request.user.userprofile

    if logged_in_user.role.values_list( 'role_name', flat=True )[0] =='admin':
        organizations= logged_in_user.organization.get_descendants( include_self=True )
    else:
        organizations= [ logged_in_user.organization ]

    return organizations

