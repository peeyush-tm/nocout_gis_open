"""
    Signals associated with service app.
"""
# Import nocout utils gateway class
from nocout.utils.util import NocoutUtilsGateway

# Create instance of 'NocoutUtilsGateway' class
nocout_utils = NocoutUtilsGateway()

from download_center.tasks import scheduled_email_report


@nocout_utils.disable_for_loaddata
def send_mail_on_report_generation(sender, instance=None, created=False, **kwargs):
    """
        Set 'is_device_change' for all site instances to 1 if protocol is modified
        Parameters:
            - sender (<class 'django.db.models.base.ModelBase'>) - sender model class
                                                                   i.e. <class 'service.models.Protocol'>
            - instance (<class 'service.models.Protocol'>) - instance being saved
                                                                     for e.g. Protocol object
            - created (bool) - object created or updated
            - kwargs (dict) - a dictionary of keyword arguments passed to constructor for e.g.
                                {
                                    'update_fields': None,
                                    'raw': False,
                                    'signal': <django.dispatch.dispatcher.Signalobjectat0x7f44749958d0>,
                                    'using': 'default'
                                }
    """
    if instance:
        report = instance.report_name
        scheduled_email_report.delay(report)