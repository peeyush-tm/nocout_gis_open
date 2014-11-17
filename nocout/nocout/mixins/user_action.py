"""
User Log Deletion Mixin to be used for class based views through-out the system.
"""
from activity_stream.models import UserAction

class UserLogDeleteMixin(object):
    """
    View mixin which log the user action on delete.

    Example Usage:

        class SomeDeleteView(UserLogDeleteMixin, DeleteView):
            ...
    """
    obj_alias = 'alias'

    def delete(self, request, *args, **kwargs):
        """
        overriding the delete method to log the user activity on deletion.
        """
        obj = self.get_object()
        model_name = self.model.__name__
        alias = getattr(obj, self.obj_alias)
        action='A {0} is deleted - {1}'.format(model_name.lower(), alias)
        UserAction.objects.create(user_id=self.request.user.id, module=model_name, action=action)
        return super(UserLogDeleteMixin, self).delete(request, *args, **kwargs)
