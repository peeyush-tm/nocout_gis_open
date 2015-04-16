from django.http import HttpResponseRedirect
from django.conf import settings
import sys


class LoginRequiredMiddleware:

    def process_request(self, request):
        # Required to debug-------------------
        # print str(request.user) +' in LoginRequiredMiddleware '+sys._getframe().f_code.co_name
        # print 'printint path %s'%str((request.path_info.lstrip('/')))
        #--------------------------
        if not request.user.is_authenticated():
            path = request.path_info.lstrip('/')
            if not(path in settings.LOGIN_EXEMPT_URLS):
                return HttpResponseRedirect( settings.LOGIN_URL + '?next=%s'%path )
