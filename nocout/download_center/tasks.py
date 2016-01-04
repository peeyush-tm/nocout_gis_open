from celery import task, group
from download_center.models import EmailReport, ReportSettings, ProcessedReportDetails
import time
from django.http import HttpRequest
from django.utils.datastructures import MultiValueDict
import logging
logger = logging.getLogger(__name__)


@task
def scheduled_email_report():
    """
    This is a celery function which will send Reports to user defined email on scheduled time
    Timing can be changed from settings.py file

    Args:
        email_report(dict) : Dictionary containing email_id as a Key and list of report_name
                             mapped to this email_id
                             for e.g.,
                             {
                                u'chanish.agarwal@teramatrix.in': [
                                    u'BSDump',
                                    u'SSDump'
                                ],
                                u'nitin.kumar@termatrix.co': [
                                    u'Modulation'
                                ],
                                u'priyesh.kumar@teramatrix.co': [
                                    u'SSDump'
                                ],
                                u'chanish.agarwal1@gmail.com': [
                                    u'customer_report'
                                ]
                            }
        reports(list) : List of report names.
                        for e.g.,
                        [u'customer_report', u'BSDump', u'SSDump', u'Modulation']

        file_path(dict) : Dictionary report_name is key and corrosponding path to that report will be value.
                          for e.g.,
                          {
                            u'Modulation': u'/apps/tmp/media/download_center/ETL/Reports/Modulation/Modulation2015Apr15.xlsx',
                            u'SSDump': u'/apps/tmp/media/download_center/ETL/Reports/SSDump/SSDump2015Apr16.xlsx',
                            u'BSDump': u'/apps/tmp/media/download_center/ETL/Reports/BSDump/BSDump2015Apr16.xlsx',
                            u'customer_report': u'/apps/tmp/media/download_center/ETL/Reports/CustomerReport/file.xlsx'
                        }
    """
    message = ''
    cur_date = time.strftime("%Y-%m-%d")
    x = EmailReport.objects.all()
    # Dictionary contains keys = email_id and values = list of report_name to be send to the email user.
    email_report = {}
    reports = list()  # List of report_name.
    for i in x:
        report_name = i.report_name.report_name
        email_list = i.email_list.split(',')
        reports.append(report_name)
        if email_list:
            for e in email_list:
                if e.strip() not in email_report:
                    email_report[e.strip()] = []
                email_report[e.strip()].append(report_name)

    # Dictionary where key will be report_name and value will be file_path based on Current Date.
    file_path = dict()
    for report in reports:
        try:
            path = ProcessedReportDetails.objects.filter(report_name=report, created_on__icontains=cur_date)[0].path
            if path:
                file_path[report] = path
        except IndexError as e:
            logger.exception(e.message)

    # Generating POST request for Email API.
    request_object = HttpRequest()
    from alarm_escalation.views import EmailSender
    email_sender = EmailSender()
    email_sender.request = request_object

    for email in email_report.keys():
        report_list = email_report[email]
        attachment_path = list()
        for report in report_list:
            try:
                attachment_path.append(file_path[report])
            except KeyError:
                message += report + ' File Not Found\n'
        try:
            email_sender.request.POST = {
                'subject': 'Scheduled email reports',
                'message': message,
                'to_email': email,
                'attachment_path': attachment_path
            }
        except Exception, e:
            pass

        email_sender.POST = {
            'subject': 'Scheduled email reports',
            'message': message,
            'to_email': email,
            'attachment_path': attachment_path
        }
        # Calling Email Api (EmailSender) POST request.
        email_sender.post(email_sender)












