import json
from actstream import action
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.contrib import auth
from django.views.decorators.csrf import csrf_protect
from django.contrib.auth.models import User
from nocout import settings
from nocout.settings import MAX_USER_LOGIN_LIMIT
from session_management.models import Visitor

@csrf_protect
def login(request):

    if not request.user.is_anonymous():
        return HttpResponseRedirect('/home/')

    return render(request, 'nocout/login.html')


def auth_view(request):

    result = {
        "success": 2,  # 0 - fail, 1 - success, 2 - exception
        "message": "Un-handled system exception has occurred. Please check with application administrator.",
        "data": {
            "meta": {},
            "objects": {}
        }
    }

    objects_values=dict(url='/login/')

    if Visitor.objects.all().__len__() >MAX_USER_LOGIN_LIMIT:
        result = {
            "success": 1,  # 0 - fail, 1 - success, 2 - exception
            "message": "Success/Fail message.",
            "data": {
                "meta": {},
                "objects": {'user_limit_exceed': True }
            }
        }

        return HttpResponse(json.dumps(result), mimetype='application/json')



    username = request.POST.get('username', '')
    password = request.POST.get('password', '')
    user = auth.authenticate(username=username, password=password)

    if user is not None and user.is_active:

        auth.login(request, user)
        next_url= '/'+ request.POST.get('next','home/')
        key_from_cookie = request.session.session_key
        if hasattr(request.user, 'visitor'):
            session_key_in_visitor_db = request.user.visitor.session_key

            if session_key_in_visitor_db != key_from_cookie:
                objects_values= dict(dialog=True, url=next_url)

            else:
                #User Log Activity
                action.send(request.user, verb=u'username : %s loggedin from server name: %s, server port: %s'\
                                 %( username, request.META.get('SERVER_NAME'), request.META.get('SERVER_PORT')))
                objects_values=dict(url=next_url)

        else:
            Visitor.objects.create( user=request.user, session_key=key_from_cookie )
            #User Log Activity
            action.send(request.user, verb=u'username : %s loggedin from server name: %s, server port: %s'\
                            %( username, request.META.get('SERVER_NAME'), request.META.get('SERVER_PORT')))
            objects_values=dict(url=next_url)

        result = {
            "success": 1,  # 0 - fail, 1 - success, 2 - exception
            "message": "Logged in successfully.",
            "data": {
                "meta": {},
                "objects": objects_values
            }
        }

    elif user is not None and not user.is_active:
        action.send(User.objects.get(pk=1), verb=u'a locked user is loggedin using username : %s from server name: %s, '
                     u'server port: %s' %(username, request.META.get('SERVER_NAME'), request.META.get('SERVER_PORT')))

        objects_values=dict(url='/login/')

        result = {
            "success": 0,  # 0 - fail, 1 - success, 2 - exception
            "message": "The account has been locked by the application administrator. \
                        Please contact application administrator to continue.",
            "data": {
                "meta": {},
                "objects": objects_values
            }
        }

    else:
        #User Log Activity
        action.send(User.objects.get(pk=1), verb=u'invalid loggedin using username : %s from server name: %s, '
                     u'server port: %s' %(username, request.META.get('SERVER_NAME'), request.META.get('SERVER_PORT')))

        objects_values=dict(url='/login/')

        result = {
            "success": 0,  # 0 - fail, 1 - success, 2 - exception
            "message": "The credentials entered can not be verified by the system. \
                        Please contact application administrator or retry",
            "data": {
                "meta": {},
                "objects": objects_values
            }
        }

    return HttpResponse(json.dumps(result), mimetype='application/json')

def logout(request):
    auth.logout(request)
    return HttpResponseRedirect(settings.LOGIN_URL)#render(request,'nocout/login.html')

