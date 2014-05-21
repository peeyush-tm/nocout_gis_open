from user_profile.models import UserProfile
from user_group.models import Organization

# context processor for showing user department in template


def user_dept_org(request):
    
    result = {}
    
    if request.user.is_authenticated():
        result = {'user_department' : 'unknown', 'user_organization' : 'unknown'}

        user_profile = UserProfile.objects.filter(username=request.user)
        
        if user_profile:
            user_department = user_profile[0].department_set.all()

            if user_department:
                user_dept = user_department[0]
                user_dept_name = user_dept.user_group.alias
                result['user_department'] = user_dept_name
                user_organization = Organization.objects.filter(user_group=user_dept.user_group_id)

                if user_organization:
                    user_org_name = user_organization[0].name

                    if hasattr(request, 'user'):
                        result ['user_organization'] = user_org_name

    return result
