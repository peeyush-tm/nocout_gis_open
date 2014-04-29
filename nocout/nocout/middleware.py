from django.db.models import signals
from django.utils.functional import curry


class UserProfileAuditMiddleware(object):
    def process_request(self, request):
        if not request.method in ('GET', 'HEAD', 'OPTIONS', 'TRACE'):
            if hasattr(request, 'user') and request.user.is_authenticated():
                user = request.user
            else:
                user = None

            audit = curry(self.audit, user)
            signals.pre_save.connect(audit, dispatch_uid=(self.__class__, request,), weak=False)

    def process_response(self, request, response):
        signals.pre_save.disconnect(dispatch_uid=(self.__class__, request,))
        return response

    def audit(self, user, sender, instance, **kwargs):
        if not getattr(instance, 'created_by_id', None):
            instance.created_by = user
        if hasattr(instance, 'updated_by_id'):
            instance.updated_by = user