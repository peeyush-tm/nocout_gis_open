from user_profile.models import UserProfile
from user_group.models import Organization

# context processor for showing user department in template
def user_department(request):
    try:
        user_profile = UserProfile.objects.get(username=request.user)
        user_department = user_profile.department_set.all()[0].user_group.alias
        print "User Department: {}".format(user_department)
    except:
        print "User doesn't exist."

    if hasattr(request, 'user'):
        try:
            return {'user_department': user_department}
        except:
            print "User profile is not set."
    return {}

# context processor for showing user department in template
def user_organization(request):
    try:
        user_profile = UserProfile.objects.get(username=request.user)
        user_group = user_profile.department_set.all()[0].user_group
        user_organization = Organization.objects.get(user_group=user_group.id).name
        print "User Organization: {}".format(user_organization)
    except:
        print "User doesn't exist."

    if hasattr(request, 'user'):
        try:
            return {'user_organization': user_organization}
        except:
            print "User pofile is not set."
    return {}


