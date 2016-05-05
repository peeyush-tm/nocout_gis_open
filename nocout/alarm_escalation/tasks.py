"""
Provide celery tasks for Alarm Escalation.

    from alarm_escalation.tasks import check_device_status

    check_device_status.delay()
"""

from celery import task, group
from django.utils import timezone
from django.utils.dateformat import format
#email
from django.core.mail import send_mail
from django.core.mail import EmailMessage, EmailMultiAlternatives
#email end
from django.conf import settings
from django.template.loader import render_to_string
import datetime
import time

from organization.models import Organization
from device.models import Device, DeviceType, DeviceTypeService, DeviceTypeServiceDataSource, DeviceTechnology
from service.models import Service, ServiceDataSource, ServiceSpecificDataSource
from performance.models import ServiceStatus
from alarm_escalation.models import EscalationStatus, EscalationLevel
# Import performance utils gateway class
from performance.utils.util import PerformanceUtilsGateway
# Import inventory utils gateway class
from inventory.utils.util import InventoryUtilsGateway
# Import inventory utils gateway class
from scheduling_management.views import SchedulingViewsGateway
from inventory.tasks import bulk_update_create
from nocout.settings import SMS_LOG_FILE_PATH, EMAIL_BACKEND, EMAIL_FILE_PATH
import re
import logging
logger = logging.getLogger(__name__)

# Create instance of 'PerformanceUtilsGateway' class
perf_utils = PerformanceUtilsGateway()

### SMS Sending
import requests
#### SMS GATEWAY SETTINGS
GATEWAY_SETTINGS = {
    'URL': 'http://121.244.239.140/csend.dll'
}
GATEWAY_PARAMETERS = {
    'Username': 'wirelessonetool',
    'Password': '12345vgsmhttp',
    'Priority': 3,
    'Commmethod': 'cellent',
    'Returnseq': 1,
    'Sender': 'TATACOMM Anil . Now',
    'N': '',
    'M': ''
}
#### SMS GATEWAY SETTINGS

# Dictionary for recognizing changing status of devices
status_dict = {
    'changed_good': {
        'old': 0,
        'new': 1
    },
    'changed_bad': {
        'old': 1,
        'new': 0
    },
    'unchanged_good': {
        'old': 1,
        'new': 1
    },
    'unchanged_bad': {
        'old': 0,
        'new': 0
    },
}

EMAIL_DATE_FORMAT = '%a, %d %b %Y %H:%M:%S' # Tue, 23 Feb 2016 09:43:15


def generate_sms_log(msg=None, phone_numbers=None, alarm=None):
    """
    This function generates SMS logs in 'SMS_LOG_FILE_PATH' directory
    """
    if msg and phone_numbers:
        try:
            ip_address = alarm.device.ip_address
        except Exception, e:
            ip_address = ''

        timestamp = time.time()
        full_time = datetime.datetime.fromtimestamp(timestamp).strftime('%Y%m%d-%H%M%S-%f')
        file_name = full_time
        if ip_address:
            file_name = '{0}_{1}'.format(full_time, ip_address)

        try:
            log_file = open(SMS_LOG_FILE_PATH + "/" + file_name + ".log", "w")
            log_file.write('Sent To: ' + str(phone_numbers) + '\n')
            log_file.write('Message: ' + str(msg))
            log_file.close()
        except Exception, e:
            logger.error(e)
            logger.error('SMS Log File Not Created')
    return True


def generate_email_log(html_msg=None, headers_info=None, alarm=None):
    """
    This function generates Email logs in 'EMAIL_FILE_PATH' directory
    """
    if html_msg and alarm:
        try:
            ip_address = alarm.device.ip_address
        except Exception, e:
            ip_address = ''

        email_headers = ''

        try:
            if headers_info.get('subject'):
                email_headers += 'Subject: {}\n'.format(headers_info.get('subject'))
        except Exception, e:
            pass

        try:
            if headers_info.get('from_email'):
                email_headers += 'From: {}\n'.format(headers_info.get('from_email'))
        except Exception, e:
            pass

        try:
            if headers_info.get('to_email'):
                email_headers += 'To: {}\n'.format(headers_info.get('to_email'))
        except Exception, e:
            pass

        try:
            if headers_info.get('email_datetime'):
                email_headers += 'Date: {}\n'.format(headers_info.get('email_datetime'))
        except Exception, e:
            pass

        timestamp = time.time()
        full_time = datetime.datetime.fromtimestamp(timestamp).strftime('%Y%m%d-%H%M%S-%f')
        file_name = full_time
        if ip_address:
            file_name = '{0}_{1}'.format(full_time, ip_address)

        try:
            log_file = open(EMAIL_FILE_PATH + "/" + file_name + ".log", "w")
            if email_headers:
                log_file.write('='*50)
                log_file.write('\n')
                log_file.write(email_headers)
                log_file.write('='*50)
                log_file.write('\n')
            log_file.write(html_msg.encode('utf-8'))
            log_file.close()
        except Exception, e:
            logger.error(e)
            logger.error('Email Log File Not Created')
    return True

def status_change(old_status, new_status):
    """
    A function for finding status of device is changed or unchanged & good or bad
    :Args:
        old_status: Integer Field (0 or 1)
        new_status: Integer Field (0 or 1)

    :return:
        status_dict : dictionary
    """

    if old_status == 0 and new_status == 0:
        # that is the old status was bad
        # that is the new status is bad itself
        return status_dict['unchanged_bad']

    elif old_status == 0 and new_status == 1:
        # that is the device has recovered
        return status_dict['changed_good']

    elif old_status == 1 and new_status == 0:
        return status_dict['changed_bad']

    elif old_status == 1 and new_status == 1:
        return status_dict['unchanged_good']

    else:
        return -1

@task
def raise_alarms(dict_devices_invent_info, service_status_list, org, required_levels):
    """
    This is celery task function which raise alarms for bad performance or good performance of device for a particular organization 
    and divide celery tasks into more tasks depends on service levels which requires escalation.

    :Args:
       dict_devices_invent_info : Indexed dict og GIS info key as device_name 
       service_status_list : List of object of services and their parameters which have escalation levels.
       org : Organizations
       required_levels : Escalation levels of particular organization.

    :return:
        True/False
    """

    # Initialization of variables.
    g_jobs = list()
    ret = False
    s_sds = ServiceSpecificDataSource.objects.prefetch_related(
        'service_data_sources',
        'service'
    ).all()

    # So that mysql can't query again and again in below loop (Data is collected in this Query set)
    escalation_status_data = EscalationStatus.objects.all()

    for service_status in service_status_list:
        # Get EscalationStatus to process.
        # if severity of service_status is 'ok', set the old_status and new_status 'Good' for defaults.
        if service_status.severity == 'ok':
            old_status = 1
            new_status = 1
        # else set the new_status and old_status 'Bad' for defaults.
        else:
            old_status = 0
            new_status = 0

        # get the service - service data source mapping
        service_service_data_source = s_sds.get(
            service__name=service_status.service_name,
            service_data_sources__name=service_status.data_source
        )
        # get the service object
        service = service_service_data_source.service
        # get the service data source object
        service_data_source = service_service_data_source.service_data_sources

        # Get relative levels to inform
        # Get the list of levels of EscalationStatus object after filtering the escalationLevel table
        # on the basis of service and service_data_source.
        service_level_list = required_levels.filter(
            service=service,
            service_data_source=service_data_source
        )

        time_now = float(format(datetime.datetime.now(), 'U'))  # in unixtime
        time_since = float(service_status.age)  # already in unixtime
        changed_time = time_now - time_since  # in seconds the time since the status has changed
        # if there are actually a level corrosponding to this alarm 
        if service_level_list.exists():
            # get the device of service_status.
            device = Device.objects.get(device_name=service_status.device_name)
            # device, device_type, service(get from service_status) and service_data_source(get from service_status).
            obj, created = escalation_status_data.get_or_create(
                device=device,
                service=service,
                service_data_source=service_data_source,
                defaults={
                    'severity': service_status.severity,
                    'old_status': old_status,
                    'new_status': new_status,
                    'status_since': datetime.datetime.fromtimestamp(float(service_status.age)),
                    'ip': service_status.ip_address,
                    'organization': org
                }
            )
            # Getting complete GIS info corresponding to that device_name
            invent_obj = dict_devices_invent_info.get(service_status.device_name)
            if not invent_obj:
                # If no gis info then iterate to next element of list
                continue

            invent_obj.update({'current_value': service_status.current_value})
            invent_obj.update({'threshold' : service_status.warning_threshold})
            if service_status.severity.lower() in ['critical', 'crit', 'down']:
                invent_obj.update({'threshold' : service_status.critical_threshold})
            
            # if object is get & not created,
            # then update the severity and ip_address of object as per the severity and ip_address of service_status.
            if not created:
                obj.severity = service_status.severity
                obj.ip = service_status.ip_address
                obj.organization = org
                obj.status_since = datetime.datetime.fromtimestamp(float(service_status.age))

                old_status = obj.old_status
                if service_status.severity == 'ok':
                    new_status = 1
                else:
                    new_status = 0

                # if there is a status change
                if status_change(old_status, new_status) != -1:
                    if status_change(old_status, new_status) == status_dict['unchanged_bad']:
                        level_list = service_level_list.filter(
                            alarm_age__lte=changed_time
                        )  # this should exists to raise any alarm
                        if level_list.exists():
                            # Appending Jobs
                            g_jobs.append(
                                alarm_status_changed.s(alarm_object=obj, levels=level_list, alarm_invent_object=invent_obj)  # call for task
                            )
                    elif status_change(old_status, new_status) == status_dict['unchanged_good']:
                        continue  # everything is fine keep on going
                    elif status_change(old_status, new_status) == status_dict['changed_bad']:
                        level_list = service_level_list.filter(
                            alarm_age__lte=changed_time
                        )  # this should exists to raise any alarm
                        if level_list.exists():
                            g_jobs.append(
                                alarm_status_changed.s(alarm_object=obj, levels=level_list, alarm_invent_object=invent_obj)  # call for task
                            )
                    elif status_change(old_status, new_status) == status_dict['changed_good']:
                        level_list = service_level_list
                        if level_list.exists():
                            # append the task 
                            g_jobs.append(
                                alarm_status_changed.s(
                                    alarm_object=obj,
                                    levels=level_list,
                                    alarm_invent_object=invent_obj,
                                    is_bad=False
                                )
                            )
                    else:
                        continue  # don't know what just happened

                obj.old_status = new_status
                obj.new_status = old_status

            elif created:  # the object has been created for the first time
                # if the object has been just created
                # check for the current status as in good or bad
                # check the levels to be notified
                if status_change(old_status, new_status) == status_dict['unchanged_bad'] \
                   or \
                   status_change(old_status, new_status) == status_dict['changed_bad']:
                    # this calls for a check for levels
                    level_list = service_level_list.filter(alarm_age__lte=changed_time)
                    # this should exists to raise any alarm
                    if level_list.exists():
                        g_jobs.append(
                            alarm_status_changed.s(alarm_object=obj, levels=level_list, alarm_invent_object=invent_obj)  # call for task
                        )
                        
            else:  # don't know what this means
                continue
        else:
            continue

    if not(g_jobs):
        return ret
    elif len(g_jobs):
        job = group(g_jobs)
        try:
            # Start the jobs
            result = job.apply_async()
            # for r in result.get():
            #     ret |= r
        except Exception as e:
            logger.exception(e.message)
        return True

    return True


@task()
def alarm_status_changed(alarm_object, levels, alarm_invent_object, is_bad=True):
    """
    This is celery task which opens another celery tasks for sending Emails & SMS & 
    also bulk update in Escalation status model that for particular whether Email, 
    SMS is sent or not.

    :Args:
        alarm_object : Object of Escalation Status model
        levels : All levels list
        alarm_invent_object : GIS Info parameters
        is_bad : Default True/False is a good alarm or a bad alarm ?

    :return:
        True/False
    """
    # Initialization of variables
    bulkyobject= list()
    g_jobs = list()
    ret = False
    for level in levels:
        changed=False
        method_to_call_email = ''
        method_to_call_phone = ''
        if getattr(alarm_object, 'l%d_email_status' % level.name) == 1:
            # this level has been notified
            if is_bad:
                continue
            else:
                method_to_call_email=alert_emails_for_good_performance
                # Setting attribute that email status
                setattr(alarm_object, 'l%d_email_status' % level.name, 0)
                changed=True
        elif getattr(alarm_object, 'l%d_email_status' % level.name) == 0:
            # this level is not notified
            if is_bad:
                method_to_call_email=alert_emails_for_bad_performance
                # Setting attribute that email status
                setattr(alarm_object, 'l%d_email_status' % level.name, 1)
                changed=True
            else:
                continue
        if getattr(alarm_object, 'l%d_phone_status' % level.name) == 1:
            # this level has been notified
            if is_bad:
                continue
            else:
                method_to_call_phone=alert_phones_for_good_performance
                # Setting attribute that SMS status
                setattr(alarm_object, 'l%d_phone_status' % level.name, 0)
                changed=True
        elif getattr(alarm_object, 'l%d_phone_status' % level.name) == 0:
            # this level is not notified
            if is_bad:
                method_to_call_phone=alert_phones_for_bad_performance
                # Setting attribute that SMS status
                setattr(alarm_object, 'l%d_phone_status' % level.name, 1)
                changed=True
            else:
                continue
        # else:
        #     continue
         
        if method_to_call_email and method_to_call_phone:
            # Appending of Jobs
            g_jobs.append(method_to_call_email.s(alarm=alarm_object, alarm_invent=alarm_invent_object, level=level ))
            g_jobs.append(method_to_call_phone.s(alarm=alarm_object, alarm_invent=alarm_invent_object, level=level ))

        # we dont have to use this beacause of line 225 @peeyush-tm Right ??
        if changed:
            bulkyobject.append(alarm_object)

    if not len(g_jobs):
        return ret
    else:
        job = group(g_jobs)
        # Start the Jobs
        result = job.apply_async()
        if len(bulkyobject):
            # Bulk update the Escalation Status model
            bulk_update_create.delay(bulky=bulkyobject,
                                     action='update',
                                     model=EscalationStatus)                
        return True


@task
def alert_emails_for_bad_performance(alarm, alarm_invent, level ):
    """
    Sends Emails for bad performance.

    :Args:
        alarm : Escalation status model object
        alarm_invent : GIS info dictionary
        level  : level object

    :return:
        True/False
    """
    context_dict = dict()
    # Calling function for getting all emails in particular level
    emails = level.get_emails()
    # Update the dictionary
    alarm_invent.update({'start_string': 'ALERT'})
    # Creation of context dictionary for passing in template
    context_dict['alarm'] = alarm
    context_dict['alarm_invent'] = alarm_invent
    context_dict['level'] = level
    context_dict['city'] = ''
    context_dict['state'] = ''
    try:
        context_dict['city'] = alarm.device.city.city_name
    except Exception, e:
        logger.error('Error in fetching device city --')
        logger.error(e)
        pass

    try:
        context_dict['state'] = alarm.device.state.state_name
    except Exception, e:
        logger.error('Error in fetching device state --')
        logger.error(e)
        pass

    subject = render_to_string('alarm_message/subject.txt', context_dict)
    subject = ''.join(subject.splitlines())
    message = render_to_string('alarm_message/bad_message.html', context_dict)
    email_datetime = datetime.datetime.now().strftime(EMAIL_DATE_FORMAT)
    header_info = {
        'date': email_datetime
    }

    msg = EmailMessage(subject, message, settings.DEFAULT_FROM_EMAIL, emails, headers=header_info)
    msg.content_subtype = "html"  # Main content is now text/html
    # Attach chart image as per current service & datasource with default timestamp
    try:
        device_name = alarm.device.device_name
        service = level.service.name
        data_source = level.service_data_source.name

        chart_img_dict = perf_utils.create_perf_chart_img(device_name, service, data_source)
        img_path = chart_img_dict.get('chart_url')
        if img_path:
            msg.attach_file(img_path)
    except Exception, e:
        pass

    msg.send()

    # If EMAIL_BACKEND is not filebased then generate email logs manually
    if EMAIL_BACKEND and 'filebased' not in EMAIL_BACKEND:
        try:
            try:
                if type(emails) == type(list()):
                    emails = ', '.join(emails)
            except Exception, e:
                pass

            logs_headers_info = {
                'from_email': settings.DEFAULT_FROM_EMAIL,
                'to_email': emails,
                'subject': subject,
                'email_datetime': email_datetime
            }
            generate_email_log(
                html_msg=message,
                headers_info=logs_headers_info,
                alarm=alarm
            )
        except Exception, e:
            logger.error('Email Log Error')
            logger.error(e)
            pass

    return True


@task
def alert_phones_for_bad_performance(alarm, alarm_invent, level):
    """
    Sends sms to phones for bad performance.

    :Args:
        alarm : Escalation status model object
        alarm_invent : GIS info dictionary
        level  : level object

    :return:
        True/False

    >>> payload = {'key1': 'value1', 'key2': 'value2'}
    >>> r = requests.get("http://httpbin.org/get", params=payload)
    """
    context_dict = dict()
    payload =  GATEWAY_PARAMETERS
    url = GATEWAY_SETTINGS['URL']
    # calling function for gettings all phone numbers in particular level
    phones = level.get_phones()
    if len(phones):
        send_to = ",".join(phones)
        alarm_invent.update({'start_string': 'ALERT'})
        # Creation of context dictionary for passing in template
        context_dict['alarm'] = alarm
        context_dict['alarm_invent'] = alarm_invent
        context_dict['level'] = level
        message = render_to_string('alarm_message/subject.txt', context_dict)
        #render_to_string('alarm_message/good_message.html', context_dict)
        payload['N'] = send_to
        payload['M'] = message
        
        try:
            generate_sms_log(
                msg=message,
                phone_numbers=send_to,
                alarm=alarm
            )
        except Exception, e:
            logger.error(e)
            logger.error('SMS Log not created')

        r = requests.get(url, params=payload)
    else:
        return False
    # message = ''
    # send_sms(subject, message, settings.DEFAULT_FROM_PHONE, phones, fail_silently=False)
    pass


@task
def alert_emails_for_good_performance(alarm, alarm_invent, level ):
    """
    Sends Emails for good performance. 

    :Args:
        alarm : Escalation status model object
        alarm_invent : GIS info dictionary
        level  : level object

    :return:
        True/False
    """
    context_dict = dict()
    # Calling function for getting all emails in particular level
    emails = level.get_emails()
    alarm_invent.update({'start_string': 'RECOVERED'})
    # Creation of context dictionary for passing in template
    context_dict['alarm'] = alarm
    context_dict['alarm_invent'] = alarm_invent
    context_dict['level'] = level
    context_dict['city'] = ''
    context_dict['state'] = ''
    try:
        context_dict['city'] = alarm.device.city.city_name
    except Exception, e:
        logger.error('Error in fetching device city --')
        logger.error(e)
        pass

    try:
        context_dict['state'] = alarm.device.state.state_name
    except Exception, e:
        logger.error('Error in fetching device state --')
        logger.error(e)
        pass
        
    subject = render_to_string('alarm_message/subject.txt', context_dict)
    subject = ''.join(subject.splitlines())
    message = render_to_string('alarm_message/good_message.html', context_dict)
    email_datetime = datetime.datetime.now().strftime(EMAIL_DATE_FORMAT)
    header_info = {
        'date': email_datetime
    }
    msg = EmailMessage(subject, message, settings.DEFAULT_FROM_EMAIL, emails, headers=header_info)
    msg.content_subtype = "html"  # Main content is now text/html
    # Attach chart image as per current service & datasource with default timestamp
    try:
        device_name = alarm.device.device_name
        service = level.service.name
        data_source = level.service_data_source.name

        chart_img_dict = perf_utils.create_perf_chart_img(device_name, service, data_source)
        img_path = chart_img_dict.get('chart_url')
        if img_path:
            msg.attach_file(img_path)
    except Exception, e:
        pass

    msg.send()

    # If EMAIL_BACKEND is not filebased then generate email logs manually
    if EMAIL_BACKEND and 'filebased' not in EMAIL_BACKEND:
        try:
            try:
                if type(emails) == type(list()):
                    emails = ', '.join(emails)
            except Exception, e:
                pass

            logs_headers_info = {
                'from_email': settings.DEFAULT_FROM_EMAIL,
                'to_email': emails,
                'subject': subject,
                'email_datetime': email_datetime
            }
            generate_email_log(
                html_msg=message,
                headers_info=logs_headers_info,
                alarm=alarm
            )
        except Exception, e:
            logger.error('Email Log Error')
            logger.error(e)
            pass

    return True


@task
def alert_phones_for_good_performance(alarm, alarm_invent, level ):
    """
    Sends sms to phones for bad performance.

    :Args:
        alarm : Escalation status model object
        alarm_invent : GIS info dictionary
        level  : level object

    :return:
        True/False
    """
    context_dict = dict()
    payload =  GATEWAY_PARAMETERS
    url = GATEWAY_SETTINGS['URL']
    # calling function for gettings all phone numbers in particular level
    phones = level.get_phones()
    if len(phones):
        send_to = ",".join(phones)
        alarm_invent.update({'start_string': 'RECOVERED'})
        context_dict['alarm'] = alarm
        context_dict['alarm_invent'] = alarm_invent
        context_dict['level'] = level
        message = render_to_string('alarm_message/subject.txt', context_dict)
        #render_to_string('alarm_message/good_message.html', context_dict)
        payload['N'] = send_to
        payload['M'] = message
        try:
            generate_sms_log(
                msg=message,
                phone_numbers=send_to,
                alarm=alarm
            )
        except Exception, e:
            logger.error('SMS Log not created')
        r = requests.get(url, params=payload)
    else:
        return False
    # message = ''
    # send_sms(subject, message, settings.DEFAULT_FROM_PHONE, phones, fail_silently=False)
    pass

@task
def check_device_status():
    """
    This is celery task function calls from settings file of project in every 5 minutes. 
    This function initializes the parameters for Escalation and brings out information of 
    complete GIS inventory for all devices and finally divide this task other task depending 
    on no. of organizations & status of devices on different database per organization.

    :Args:
        No inout Arguments.

    :return:
        True/False
    """
    # Initialization of variables
    g_jobs = list()
    ret = False
    service_list = []
    service_data_source_list = []

    # Create instance of 'InventoryUtilsGateway' class
    inventory_utils = InventoryUtilsGateway()

    # Create instance of 'SchedulingViewsGateway' class
    scheduling_utils = SchedulingViewsGateway()

    #get the device list which is in downtime scheduling today.
    device_id_list = scheduling_utils.get_today_event_list()['device_ids']
    for org in Organization.objects.all():
        # get the objects which require escalation
        required_objects = EscalationLevel.objects.filter(organization__in=[org])
        # if there is actually an escalation object defined
        # if there is none dont worry & return True & relax
        if required_objects.exists():
            # Extract service list, service data source list, device type list from objects which requires escalation
            device_type_list = set(required_objects.values_list('device_type__id', flat=True))
            service_list = set(required_objects.values_list('service__name', flat=True))
            service_data_source_list = set(required_objects.values_list('service_data_source__name', flat=True))

            # exclude those devices which is in downtime scheduling today.
            device_list_qs = Device.objects.filter(
                organization__in=[org],
                device_type__in=device_type_list,
                is_added_to_nms__gt=0
            ).exclude(id__in=device_id_list).values('device_name', 'machine__name')

            # Prepare list of dictionaries {key = machine_name : value = list of devices}
            machine_dict = prepare_machines(device_list_qs)

            # Call 'prepare_gis_devices' method of 'PerformanceUtilsGateway' class
            # this class gives us complete information of GIS inventory related to all devices.
            list_devices_invent_info = perf_utils.prepare_gis_devices(device_list_qs, page_type=None)
            # Conversion of list to indexed dict so that dict.get('device_name') gives us complete GIS info corresponding to that device name.
            dict_devices_invent_info = inventory_utils.list_to_indexed_dict(list_devices_invent_info, 'device_name')

            for machine_name, device_list in machine_dict.items():
                service_status_list = ServiceStatus.objects.filter(
                    device_name__in=device_list,
                    service_name__in=service_list,
                    data_source__in=service_data_source_list,
                    ip_address__isnull=False
                ).using(alias=machine_name)

                if service_status_list.exists():
                    # Appending jobs
                    g_jobs.append(
                        raise_alarms.s(dict_devices_invent_info,
                                       service_status_list=service_status_list,
                                       org=org,
                                       required_levels=required_objects
                        )
                    )

    if not len(g_jobs):
        return ret

    job = group(g_jobs)
    # Start the jobs
    result = job.apply_async()
    # for r in result.get():
    #     ret |= r

    return True

def prepare_machines(device_list_qs):
    """
    Return dict of machine name keys containing values of related devices list.

    :Args:
        device_list_qs : list of dictionaries of devices info 

    :return:
        machine_dict : dictionary {key = machine name : value = list of devices}
    """
    unique_device_machine_list = {device['machine__name']: True for device in device_list_qs}.keys()

    machine_dict = {}
    for machine in unique_device_machine_list:
        machine_dict[machine] = [device['device_name'] for device in device_list_qs if device['machine__name'] == machine]
    return machine_dict


def prepare_services(device_list_qs):
    """
    Return list of services of device types.

    :Args:
        device_list_qs:

    :return:
        service_name_list:
    """
    device_type_list = DeviceType.objects.filter(id__in=device_list_qs.values_list('device_type', flat=True))
    return list(DeviceTypeService.objects.filter(
        device_type__in=device_type_list).values_list('service__name', flat=True)
    )


def prepare_service_data_sources(service_name_list):
    """
    Return list of service data sources of services.

    :Args:
        service_name_list : List of service names

    :return:
        data_source_name_list : List of service data sources
    """
    return list(DeviceTypeServiceDataSource.objects.filter(
        device_type_service__service__name__in=service_name_list).values_list('service_data_sources__name', flat=True)
    )


@task
def mail_send(result):
    """
    This is a Celery function which send mail for given parameters(valid and checked)
    used If Else for case of attachments availability

    Args:
        result (dict): Dictionary containing email data.
                       For e.g.,
                            {
                                "message": "Successfully send the email.",
                                "data": {
                                    "to_email": [
                                        "chanishagarwal0@gmail.com"
                                    ],
                                    "attachments": [
                                        "EmailAPI.docx",
                                        "IMG-20151020-WA0000.jpg"
                                    ],
                                    "from_email": "chanish.agarwal1@gmail.com",
                                    "attachment_path": [
                                        "/home/chanish/Desktop/chart-35-02.png"
                                    ],
                                    "message": "Please find attachmetn Below",
                                    "subject": "Warning system is getting slow"
                                },
                                "success": 1
                            }
    """
    mail = EmailMessage(result['data']['subject'], result['data']['message'],
                        result['data']['from_email'],
                        result['data']['to_email'])
    # Handling mail without an attachment.
    if result['data']['attachments']:
        for attachment in result['data']['attachments']:
            mail.attach(attachment.name, attachment.read(), attachment.content_type)

    if result['data']['attachment_path']:
        for files in result['data']['attachment_path']:
            if re.search('^http.*', files):
                pass
            else:
                mail.attach_file(files)

    mail.send()
