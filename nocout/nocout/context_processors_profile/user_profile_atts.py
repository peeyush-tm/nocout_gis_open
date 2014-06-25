from user_profile.models import UserProfile
from user_group.models import Organization

# context processor for showing user department in template


def user_dept_org(request):
    result = {}
    if request.user.is_authenticated():
        result['user_organization']=request.user.userprofile.organization.alias
    return result
