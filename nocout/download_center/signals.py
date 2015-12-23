"""
    Signals associated with download_center app.
"""
# Import nocout utils gateway class
from nocout.utils.util import NocoutUtilsGateway

# Create instance of 'NocoutUtilsGateway' class
nocout_utils = NocoutUtilsGateway()

from download_center.tasks import scheduled_email_report


@nocout_utils.disable_for_loaddata
def send_mail_on_report_generation(sender, instance=None, created=False, **kwargs):

    if instance:
        report = instance.report_name
        scheduled_email_report.delay(report)