# context processor for showing user department in template


def user_dept_org(request):
    result = {}
    if request.user.is_authenticated() and hasattr(request.user, 'userprofile'):
            result['user_organization']=request.user.userprofile.organization.alias
    return result
