"""
User Log Deletion Mixin to be used for class based views through-out the system.
"""
from activity_stream.models import UserAction
import logging
logger = logging.getLogger(__name__)

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
        if model_name == 'Sector':
            try:
                sector_configured_on = getattr(obj, 'sector_configured_on')
                sector_device_ip = sector_configured_on.ip_address
            except Exception as e:
                sector_device_ip = ' '
                logger.info("Sector Configured not present Exception: ", e.message)
            try:   
                bs_name_id = getattr(obj, 'base_station')
                bs_name = bs_name_id.alias
            except Exception as e:
                bs_name = ' '
                logger.info("Base Name is not present Exception: ", e.message)
            try:
                sector_id = getattr(obj, 'sector_id')
            except Exception as e:
                sector_id = ''
                logger.info("Sector ID is not present Exception: ", e.message)
            action = 'A {0} is deleted BS Name-{1}, Sector ID-{2}, IP Address-{3} '.format(model_name.lower(), bs_name, sector_id, sector_device_ip)
        else:
            alias = getattr(obj, self.obj_alias)
            action='A {0} is deleted - {1}'.format(model_name.lower(), alias)
        UserAction.objects.create(user_id=self.request.user.id, module=model_name, action=action)
        return super(UserLogDeleteMixin, self).delete(request, *args, **kwargs)
