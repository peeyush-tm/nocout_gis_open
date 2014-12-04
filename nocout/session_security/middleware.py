"""
SessionSecurityMiddleware is the heart of the security that this application
attemps to provide.

To install this middleware, add to your ``settings.MIDDLEWARE_CLASSES``::

    'session_security.middleware.SessionSecurityMiddleware'

Make sure that it is placed **after** authentication middlewares.
"""

import time
from datetime import datetime, timedelta

from django import http
from django.contrib.auth import logout
from django.core.urlresolvers import reverse
from django.utils import timezone

from .utils import get_last_activity, set_last_activity
from .settings import EXPIRE_AFTER, PASSIVE_URLS


class SessionSecurityMiddleware(object):
    """
    In charge of maintaining the real 'last activity' time, and log out the
    user if appropriate.
    """

    def process_request(self, request):
        """ Update last activity time or logout. """
        if not request.user.is_authenticated():
            return

        # If user is already logged in another session.
        # Also has logged in using current session (skipping dialog box)
        # Log-out user from current session.
        if hasattr(request.user, 'visitor'):
            key_from_cookie = request.session.session_key
            session_key_in_visitor_db = request.user.visitor.session_key

            # If user has not changed password after first time login
            # And trying to access closing pop-up dialog then logout
            is_first_time_login = False if request.user.userprofile.password_changed_at else True
            if request.path != '/user/change_password/' and is_first_time_login:
                logout(request)

            if request.user.userprofile.password_changed_at:
                password_changed_at = request.user.userprofile.password_changed_at
                is_password_expired = password_changed_at + timedelta(days=30) < timezone.now()
                if is_password_expired and request.path != '/user/change_password/':
                    logout(request)

            if session_key_in_visitor_db != key_from_cookie and request.path != '/sm/dialog_action/':
                logout(request)

        now = datetime.now()
        self.update_last_activity(request, now)

        delta = now - get_last_activity(request.session)
        if delta >= timedelta(seconds=EXPIRE_AFTER):
            logout(request)
        elif request.path not in PASSIVE_URLS:
            set_last_activity(request.session, now)

    def update_last_activity(self, request, now):
        """
        If ``request.GET['idleFor']`` is set, check if it refers to a more
        recent activity than ``request.session['_session_security']`` and
        update it in this case.
        """
        if '_session_security' not in request.session:
            set_last_activity(request.session, now)

        last_activity = get_last_activity(request.session)
        server_idle_for = (now - last_activity).seconds

        if (request.path == reverse('session_security_ping') and
                'idleFor' in request.GET):
            # Gracefully ignore non-integer values
            try:
                client_idle_for = int(request.GET['idleFor'])
            except ValueError:
                return

            # Disallow negative values, causes problems with delta calculation
            if client_idle_for < 0:
                client_idle_for = 0

            if client_idle_for < server_idle_for:
                # Client has more recent activity than we have in the session
                last_activity = now - timedelta(seconds=client_idle_for)

                # Update the session
                set_last_activity(request.session, last_activity)
