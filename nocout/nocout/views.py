import json
from django.core.cache import cache
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.contrib import auth
from django.views.decorators.csrf import csrf_protect
from django.views.generic.base import View
from django.contrib.auth.models import User
from nocout import settings
from session_management.models import Visitor, AuthToken
from datetime import timedelta
from django.utils import timezone

##error pages
from django.shortcuts import render_to_response
from django.template import RequestContext
##error pages
from activity_stream.models import UserAction
from user_profile.models import UserProfile
import logging

logger = logging.getLogger(__name__)

from inventory.models import LivePollingSettings, ThematicSettings, UserThematicSettings, ThresholdConfiguration
from device.models import DeviceTypeService



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


class AuthView(View):
    """
    """
    def post(self, request):
        '''
        :type request: django request object
        '''
        result = self.get_result(success=2,
                                message="Un-handled system exception has occurred. \
                                Please check with application administrator.")
        user_audit = self.get_user_audit(action="Login Attempt from IP address")

        # Visitor limit should not be exceed.
        self.check_visitor_limit()

        # check the authentication of the requested user.
        username = request.POST.get('username', '')
        password = request.POST.get('password', '')
        user = auth.authenticate(username=username, password=password)

        if user is not None:
            if user.is_staff:
                return HttpResponse(json.dumps(result), content_type='application/json')

            if not user.is_active or user.userprofile.is_deleted:
                response = self.invalid_user(user)
                result = response['result']
                user_audit = response['user_audit']
            else:
                result = self.valid_user(user)
                user_audit = self.get_user_audit(user_id=user.id, action="Logged in successfully.")

        else:
            objects_values=dict(reason="The credentials entered can not be verified by the system. \
                                        Please contact application administrator or retry")
            result = self.get_result(success=0, objects_values=objects_values,
                                    message="Invalid Credentials")
            user_audit = self.get_user_audit(action="login attempt failed from IP address")

            user_profile = UserProfile.objects.filter(username=username)
            if user_profile.exists() and not user_profile[0].is_superuser and user_profile[0].is_active:
                result = self.update_userprofile(user_profile)

        try:
            UserAction.objects.create(user_id=user_audit["userid"], module=user_audit["module"],
                                    action=user_audit["action"])
        except Exception as general_exception:
            if settings.DEBUG:
                logger.error(general_exception)
            pass  # log nothing

        return HttpResponse(json.dumps(result), content_type='application/json')

    def check_visitor_limit(self):
        '''
        '''
        if Visitor.objects.count() > settings.MAX_USER_LOGIN_LIMIT:
            objects_values = dict(data={
                            "reason": "Maximum number of concurrent users logged in have exceeded, Please Wait.",
                            "user_limit_exceed": True
                            } )
            result = self.get_result(success=0, objects_values=objects_values,
                                    message="Limit for Maximum concurrent users have reached.")
            return HttpResponse(json.dumps(result), content_type='application/json')

    def invalid_user(self, user):
        '''
        '''
        if not user.is_active:
            # unlock user after 30 minutes if user locked due to invalid password attempt.
            lock_time = user.userprofile.user_invalid_attempt_at
            if lock_time and (user.userprofile.user_invalid_attempt >= 5 ):
                unlock_time = lock_time + timedelta(minutes=30)
                if timezone.now() > unlock_time:
                    user.userprofile.user_invalid_attempt = 0
                    user.userprofile.user_invalid_attempt_at = None
                    user.userprofile.save()
                    user.is_active = True
                    user.save()

                    result = self.valid_user(user) # now login the request user.
                    user_audit = self.get_user_audit(user_id=user.id, action="Logged in successfully.")
                    return {'result': result, 'user_audit': user_audit}

            user_reason = 'locked'

        elif user.userprofile.is_deleted:
            user_reason = 'deleted'

        objects_values = dict(reason="The account has been %s by the application administrator. \
                                        Please contact application administrator to continue."
                                        % (user_reason))
        result = self.get_result(success=0, message="Account %s By Administrator" % (user_reason.title()),
                                objects_values=objects_values)
        user_audit = self.get_user_audit(action="a %s user is loggedin from IP address" % (user_reason))

        return {'result': result, 'user_audit': user_audit}

    def valid_user(self, user):
        '''
        '''
        next_url = '/' + self.request.POST.get('next', 'home/')
        if 'logout' in next_url:
            next_url = settings.LOGIN_REDIRECT_URL

        # get the user's auth token.
        auth_token = self.get_auth_token(user)

        profile_status = self.userprofile_status(user)
        if profile_status['password_expire'] or not profile_status['already_logged']:
            objects_values = dict(dialog=True, url=next_url, user_id=user.id,
                                username=user.username, auth_token=auth_token)
            result = self.get_result(success=3, objects_values=objects_values,
                                    message="Logged in successfully.")
        else:
            pwd_exp_alert = profile_status['password_expire_alert']
            pwd_exp_on = profile_status['password_expires_on']

            objects_values = dict(  url=next_url, auth_token=auth_token,
                                    password_expire_alert=pwd_exp_alert,
                                    password_expires_on=unicode(pwd_exp_on.date()) )

            if hasattr(user, 'visitor'):
                session_key_in_visitor_db = user.visitor.session_key

                if session_key_in_visitor_db:
                    objects_values.update({'dialog': True})

            else:
                auth.login(self.request, user)
                Visitor.objects.create(user=self.request.user, session_key=self.request.session.session_key)
                UserProfile.objects.filter(id=user.id).update(user_invalid_attempt=0)   # empty the user invalid attempts on successful login

            result = self.get_result(success=1, message="Logged in successfully.",
                                    objects_values=objects_values)

        return result

# <<<<<<< HEAD
#     if user is not None:
#         if user.is_staff:
#             return HttpResponse(json.dumps(result), content_type='application/json')
#
# =======
    def userprofile_status(self, user):
        '''
        '''
# >>>>>>> dev_main
        already_logged = user.userprofile.password_changed_at
        password_expire = True
        password_expire_alert = False
        password_expires_on = already_logged
        if already_logged:
            password_expires_on = already_logged + timedelta(days=30)
            password_expire = password_expires_on < timezone.now()
            password_expire_alert = already_logged + timedelta(days=20) < timezone.now()

        return {'already_logged': already_logged, 'password_expire': password_expire,
                'password_expires_on': password_expires_on, 'password_expire_alert': password_expire_alert}

    def get_auth_token(self, user):
        '''
        '''
        obj, created = AuthToken.objects.get_or_create(user=user)
        if created:
            auth_token = obj.key
        else:
            AuthToken.objects.get(user=user).delete()
            user_obj = AuthToken.objects.create(user=user)
            auth_token = user_obj.key

        return auth_token

    def update_userprofile(self, user_profile):
        '''
        '''
        user_profile.update(user_invalid_attempt=user_profile[0].user_invalid_attempt+1)
        objects_values=dict(reason="The credentials entered can not be verified by the system. \
                                        Please contact application administrator or retry")
        result = self.get_result(success=0, objects_values=objects_values,
                                message="Invalid Credentials")

        if user_profile[0].user_invalid_attempt == 3:
            objects_values=dict(reason="The user will be locked if next two password are wrong.")
            result = self.get_result(success=0, message="Two Attempts Remaining",
                                    objects_values=objects_values)

        elif user_profile[0].user_invalid_attempt == 5:
            user_profile.update(is_active=False, user_invalid_attempt_at=timezone.now())

            objects_values=dict(reason="The account has been locked by the application administrator. \
                                    Please contact application administrator to continue.")
            result = self.get_result(success=0, message="Account Locked By Administrator",
                                    objects_values=objects_values)

        return result

    def get_result(self, success, message, objects_values=dict()):
        '''
        '''
        result = {
            "success": success,  # 0 - fail, 1 - success, 2 - exception
            "message": message,
            "data": {
                "meta": {},
                "objects": objects_values,
            }
        }

        return result

    def get_user_audit(self, user_id=None, module="auth", action='IP address'):
        '''
        '''
        userid = user_id if user_id else User.objects.get(pk=1).id
        action = action + '- %s' % (get_client_ip(self.request))
        user_audit = {
            "userid": userid,
            "module": module,
            "action": action
        }

        return user_audit


def logout(request):
    """
    Logout the logged in user.
    """
    try:
        user_audit = {
            "userid": request.user.id,
            "module": "auth",
            "action":"Logout",
        }
        UserAction.objects.create(user_id=user_audit['userid'], module=user_audit['module'],
                                    action=user_audit['action'])
    except:
        #dont log in case of exception
        pass
    auth.logout(request)
    return HttpResponseRedirect(settings.LOGIN_URL)


def reset_cache(request):
    """
    Clear complete cache.
    """

    cache.clear()
    return HttpResponse(json.dumps({'code': 0, 'message': 'Cache has been cleared.'}), content_type='application/json')


def updateThematicType(request):

    ds_obj = DeviceTypeService.objects.all().values('service_id', 'device_type_id')

    # Update device type in LivePollingSettings model
    for obj in ds_obj:
        service_id = obj.get('service_id')
        device_type_id = obj.get('device_type_id')
        lp_obj = LivePollingSettings.objects.filter(service_id=service_id)
        if lp_obj.exists():
            for lp in lp_obj:
                lp.device_type_id = device_type_id
                lp.save()

    
    thematic_settings_object = ThematicSettings.objects.filter(
                                   id__in=UserThematicSettings.objects.values_list('thematic_template', flat=True)
                               ).values(
                                   'id',
                                   'threshold_template__live_polling_template__technology__id',
                                   'threshold_template__live_polling_template__device_type__id'
                               )
    # Update device type in UserThematicSettings model
    for thematics in thematic_settings_object:
        device_type = thematics.get('threshold_template__live_polling_template__device_type__id')
        device_tech = thematics.get('threshold_template__live_polling_template__technology__id')
        template_id = thematics.get('id')

        user_thematics_obj = UserThematicSettings.objects.filter(
            thematic_technology_id=device_tech,
            thematic_template_id=template_id
        )
        if user_thematics_obj.exists():
            for user_thematic in user_thematics_obj:
                user_thematic.thematic_type_id = device_type
                user_thematic.save()



    return HttpResponse(json.dumps({'success': 1, 'message': 'Thematics Updated.'}), content_type='application/json')