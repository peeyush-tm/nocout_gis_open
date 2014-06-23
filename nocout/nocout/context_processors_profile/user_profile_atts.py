from user_profile.models import UserProfile
from user_group.models import Organization

# context processor for showing user department in template


def user_dept_org(request):
    
    result = {}
    
    if request.user.is_authenticated():
        result = {'user_department' : 'unknown', 'user_organization' : 'unknown'}
        #TODO: DISPLAY user group and organisation
        #store in session as well
    return result