import json
from actstream import action
from django.conf import settings
from django.contrib.sessions.models import Session
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render
from django.contrib import auth
from django.views.decorators.csrf import csrf_protect
from django.contrib.auth.models import User
from session_management.models import Visitor
from django.db.models.signals import pre_delete

@csrf_protect
def login(request):
    return render(request, 'nocout/login.html')


def auth_view(request):

        username = request.POST.get('username', '')
        password = request.POST.get('password', '')
        user = auth.authenticate(username=username, password=password)

        if user is not None:
            auth.login(request, user)

            key_from_cookie = request.session.session_key
            if hasattr(request.user, 'visitor'):
                session_key_in_visitor_db = request.user.visitor.session_key

                if session_key_in_visitor_db != key_from_cookie:

                    result={
                                "success": 1,     # 0 - fail, 1 - success, 2 - exception
                                "message": "Success/Fail message.",
                                "data": {
                                    "meta": {},
                                    "objects": {
                                         'dialog':True
                                                }
                                        }
                          }

                    return HttpResponse(json.dumps(result), mimetype='application/json')
                else:
                    #User Log Activity
                    action.send(request.user, verb=u'username : %s loggedin from server name: %s, server port: %s'\
                                     %( username, request.META.get('SERVER_NAME'), request.META.get('SERVER_PORT')))

                    result={
                                "success": 1,     # 0 - fail, 1 - success, 2 - exception
                                "message": "Success/Fail message.",
                                "data": {
                                    "meta": {},
                                    "objects": {
                                         'url':'/home/',
                                                }
                                        }
                          }

                    return HttpResponse(json.dumps(result), mimetype='application/json')
            else:
                Visitor.objects.create( user=request.user, session_key=key_from_cookie )
                #User Log Activity
                action.send(request.user, verb=u'username : %s loggedin from server name: %s, server port: %s'\
                                %( username, request.META.get('SERVER_NAME'), request.META.get('SERVER_PORT')))
                result={
                                "success": 1,     # 0 - fail, 1 - success, 2 - exception
                                "message": "Success/Fail message.",
                                "data": {
                                    "meta": {},
                                    "objects": {
                                         'url':'/home/',
                                                }
                                        }
                          }
                return HttpResponse(json.dumps(result), mimetype='application/json')
        else:
            #User Log Activity
            action.send(User.objects.get(pk=1), verb=u'invalid loggedin using username : %s from server name: %s, '
                         u'server port: %s' %(username, request.META.get('SERVER_NAME'), request.META.get('SERVER_PORT')))
            result={
                                "success": 1,     # 0 - fail, 1 - success, 2 - exception
                                "message": "Success/Fail message.",
                                "data": {
                                    "meta": {},
                                    "objects": {
                                         'url':'/login/',
                                                }
                                        }
                          }

            return HttpResponse(json.dumps(result), mimetype='application/json')

def logout(request):
    auth.logout(request)
    return HttpResponseRedirect(settings.LOGIN_URL)#render(request,'nocout/login.html')

