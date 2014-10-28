import json
from actstream import action
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.contrib import auth
from django.views.decorators.csrf import csrf_protect
from django.contrib.auth.models import User
from nocout import settings
from session_management.models import Visitor

##error pages
from django.shortcuts import render_to_response
from django.template import RequestContext
##error pages
from activity_stream.models import UserAction
import logging

logger = logging.getLogger(__name__)



##error pages
def handler404(request):
    response = render_to_response('nocout/404.html', {},
                                  context_instance=RequestContext(request))
    response.status_code = 404
    return response

##error pages
def handler500(request):
    response = render_to_response('nocout/500.html', {},
                                  context_instance=RequestContext(request))
    response.status_code = 500
    return response

##error pages
def handler403(request):
    response = render_to_response('nocout/403.html', {},
                                  context_instance=RequestContext(request))
    response.status_code = 403
    return response


@csrf_protect
def login(request):
    """

    :param request:
    :return:
    """
    if not request.user.is_anonymous():
        return HttpResponseRedirect('/home/')

    return render(request, 'nocout/login.html')


def get_client_ip(request):
    """
    get the client ip from the request

    :param request:
    """
    remote_address = request.META.get('REMOTE_ADDR')
    # set the default value of the ip to be the REMOTE_ADDR if available
    # else None
    ip = remote_address
    # try to get the first non-proxy ip (not a private ip) from the
    # HTTP_X_FORWARDED_FOR
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        proxies = x_forwarded_for.split(',')
        # remove the private ips from the beginning
        while len(proxies) > 0 and proxies[0].startswith(settings.PRIVATE_IPS_PREFIX):
            proxies.pop(0)
        # take the first ip which is not a private one (of a proxy)
        if len(proxies) > 0:
            ip = proxies[0]

    return ip


def auth_view(request):
    """

    :type request: django request object
    """
    result = {
        "success": 2,  # 0 - fail, 1 - success, 2 - exception
        "message": "Un-handled system exception has occurred. Please check with application administrator.",
        "data": {
            "meta": {},
            "objects": {}
        }
    }

    user_audit = {
        "userid": User.objects.get(pk=1).id,
        "module":"auth",
        "action": "Login Attempt",
    }

    objects_values = dict(url='/login/')

    if Visitor.objects.all().__len__() > settings.MAX_USER_LOGIN_LIMIT:
        result = {
            "success": 0,  # 0 - fail, 1 - success, 2 - exception
            "message": "Limit for Maximum concurrent users have reached.",
            "data": {
                "meta": {},
                "objects": {
                    "data": {
                        "reason": "Maximum number of concurrent users logged in have exceeded, Please Wait.",
                        'user_limit_exceed': True
                    }
                }
            }
        }

        return HttpResponse(json.dumps(result), mimetype='application/json')

    username = request.POST.get('username', '')
    password = request.POST.get('password', '')
    user = auth.authenticate(username=username, password=password)

    if user is not None and user.is_active:

        auth.login(request, user)
        next_url = '/' + request.POST.get('next', 'home/')
        key_from_cookie = request.session.session_key
        if hasattr(request.user, 'visitor'):
            session_key_in_visitor_db = request.user.visitor.session_key

            if session_key_in_visitor_db != key_from_cookie:
                objects_values = dict(dialog=True, url=next_url)

            else:
                objects_values = dict(url=next_url)

        else:
            Visitor.objects.create(user=request.user, session_key=key_from_cookie)
            objects_values = dict(url=next_url)

        # values to store in user audit logs
        user_audit = {
            "userid": request.user.id,
            "module": "auth",
            "action": "loggedin from IP address : %s"
                    % (get_client_ip(request)),
        }

        result = {
            "success": 1,  # 0 - fail, 1 - success, 2 - exception
            "message": "Logged in successfully.",
            "data": {
                "meta": {},
                "objects": objects_values
            }
        }

    elif user is not None and not user.is_active:
        # values to store in user audit logs
        user_audit = {
            "userid": User.objects.get(pk=1).id,
            "module": "auth",
            "action": "a locked user is loggedin from IP address %s, "
                    % (get_client_ip(request))
        }

        result = {
            "success": 0,  # 0 - fail, 1 - success, 2 - exception
            "message": "Account Locked By Administrator",
            "data": {
                "meta": {},
                "objects": {
                    "reason": "The account has been locked by the application administrator. \
                                            Please contact application administrator to continue.",
                }
            }
        }

    else:
        # User Log Activity

        # values to store in user audit logs
        user_audit = {
            "userid": User.objects.get(pk=1).id,
            "module": "auth",
            "action": "login attempt failed from IP address %s "
                    % (get_client_ip(request))
        }

        result = {
            "success": 0,  # 0 - fail, 1 - success, 2 - exception
            "message": "Invalid Credentials",
            "data": {
                "meta": {},
                "objects": {
                    "reason": "The credentials entered can not be verified by the system. \
                                            Please contact application administrator or retry",
                }
            }
        }

    try:
        UserAction.objects.create(user_id=user_audit["userid"], module=user_audit["module"],
                                    action=user_audit["action"])
    except Exception as general_exception:
        if settings.DEBUG:
            logger.error(general_exception)
        pass  # log nothing

    return HttpResponse(json.dumps(result), mimetype='application/json')


def logout(request):
    """
    Logout the logged in user.
    """
    try:
        user_audit = {
            "user": request.user,
            "verb": u'username : %s : Logoff '% (request.user.username)
        }
        action.send(user_audit["user"], verb=user_audit["verb"])
    except:
        #dont log in case of exception
        pass
    auth.logout(request)
    return HttpResponseRedirect(settings.LOGIN_URL)

