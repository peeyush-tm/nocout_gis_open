"""
Provide celery tasks for Alarm Escalation.

    from alarm_escalation.tasks import check_device_status

    check_device_status.delay()
"""

from celery import task, group
from django.utils import timezone
from django.utils.dateformat import format
from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string
import datetime

from organization.models import Organization
from device.models import Device, DeviceType, DeviceTypeService, DeviceTypeServiceDataSource, DeviceTechnology
from service.models import Service, ServiceDataSource, ServiceSpecificDataSource
from performance.models import ServiceStatus
from alarm_escalation.models import EscalationStatus, EscalationLevel

from inventory.utils import util as inventory_utils
from scheduling_management.views import get_today_event_list
from inventory.tasks import bulk_update_create
import logging
logger = logging.getLogger(__name__)



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


def status_change(old_status, new_status):
    """

    :param old_status:
    :param new_status:
    :return:
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
def raise_alarms(service_status_list, org, required_levels):
    """
    Raise alarms for bad performance or good performance of device for a particular organization.
    """
    # bulky_update = list()  # list of escalation objects we want to update
    # bulky_create = list()  # list of escalation objects we want to create

    g_jobs = list()
    ret = False
    # new_data_create = list()
    data_update = list()
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

        # get the device of service_status.
        device = Device.objects.get(device_name=service_status.device_name)
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
        # on the basis of device_type, service and service_data_source.
        service_level_list = required_levels.filter(
            service=service,
            service_data_source=service_data_source
        )

        time_now = float(format(datetime.datetime.now(), 'U'))  # in unixtime
        time_since = float(service_status.age)  # already in unixtime
        changed_time = time_now - time_since  # in seconds the time since the status has changed

        if service_level_list.exists():  # if there are actually a level corrosponding to this alarm - lets talk
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
            # if object is get & not created,
            # then update the severity and ip_address of object as per the severity and ip_address of service_status.
            if not created:
                obj.severity = service_status.severity
                obj.ip = service_status.ip_address
                obj.organization = org

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
                            g_jobs.append(
                                alarm_status_changed.s(alarm_object=obj, levels=level_list)  # call for task
                            )
                    elif status_change(old_status, new_status) == status_dict['unchanged_good']:
                        continue  # everything is fine # keep on going
                    elif status_change(old_status, new_status) == status_dict['changed_bad']:
                        level_list = service_level_list.filter(
                            alarm_age__lte=changed_time
                        )  # this should exists to raise any alarm
                        if level_list.exists():
                            g_jobs.append(
                                alarm_status_changed.s(alarm_object=obj, levels=level_list)  # call for task
                            )
                    elif status_change(old_status, new_status) == status_dict['changed_good']:
                        level_list = service_level_list
                        if level_list.exists():
                            g_jobs.append(
                                alarm_status_changed.s(
                                    alarm_object=obj,
                                    levels=level_list,
                                    is_bad=False
                                )
                            )  # append the task
                    else:
                        continue  # don't know what just happened

                obj.old_status = new_status
                obj.new_status = old_status
                data_update.append(obj)
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
                            alarm_status_changed.s(alarm_object=obj, levels=level_list)  # call for task
                        )

            else:  # don't know what this means
                continue
        else:
            continue

    if len(data_update):
        bulk_update_create.delay(bulky=data_update,
                                 action='update',
                                 model=EscalationStatus)
    else:
        pass

    if not(g_jobs):
        return ret
    elif len(g_jobs):
        job = group(g_jobs)
        try:
            result = job.apply_async()
            # for r in result.get():
            #     ret |= r
        except Exception as e:
            logger.exception(e.message)
        return True

    return True


@task()
def alarm_status_changed(alarm_object, levels, is_bad=True):
    """


    :param is_bad: is a good alarm or a bad alarm ?
    :param alarm_object:
    :param levels:
    :return:
    """
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
                # alert_emails_for_good_performance.delay(alarm=alarm_object, level=level)
                setattr(alarm_object, 'l%d_email_status' % level.name, 0)
                changed=True
        elif getattr(alarm_object, 'l%d_email_status' % level.name) == 0:
            # this level is not notified
            if is_bad:
                method_to_call_email=alert_emails_for_bad_performance
                # alert_emails_for_bad_performance.delay(alarm=alarm_object, level=level)
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
                # alert_phones_for_good_performance.delay(alarm=alarm_object, level=level)
                setattr(alarm_object, 'l%d_phone_status' % level.name, 0)
                changed=True
        elif getattr(alarm_object, 'l%d_phone_status' % level.name) == 0:
            # this level is not notified
            if is_bad:
                method_to_call_phone=alert_phones_for_bad_performance
                # alert_phones_for_bad_performance.delay(alarm=alarm_object, level=level)
                setattr(alarm_object, 'l%d_phone_status' % level.name, 1)
                changed=True
            else:
                continue
        # else:
        #     continue
         
        if method_to_call_email and method_to_call_phone:
            g_jobs.append(method_to_call_email.s(alarm=alarm_object, level=level))
            g_jobs.append(method_to_call_phone.s(alarm=alarm_object, level=level))
        # alarm_object.save()
        if changed:
            bulkyobject.append(alarm_object)

    if len(bulkyobject):
        bulk_update_create.delay(bulky=bulkyobject,
                                 action='update',
                                 model=EscalationStatus)

    if not len(g_jobs):
        return ret
    else:
        job = group(g_jobs)
        result = job.apply_async()
        return True


@task
def alert_emails_for_bad_performance(alarm, level):
    """
    Sends Emails for bad performance.
    """
    emails = level.get_emails()
    context_dict = {'alarm' : alarm}
    context_dict['level'] = level
    subject = render_to_string('alarm_message/subject.txt', context_dict)
    subject = ''.join(subject.splitlines())
    message = render_to_string('alarm_message/bad_message.html', context_dict)
    send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, emails, fail_silently=False)
    return True


@task
def alert_phones_for_bad_performance(alarm, level):
    """
    Sends sms to phones for bad performance.
    """
    phones = level.get_phones()
    # message = ''
    # send_sms(subject, message, settings.DEFAULT_FROM_PHONE, phones, fail_silently=False)
    pass


@task
def alert_emails_for_good_performance(alarm, level):
    """
    Sends Emails for good performance.
    """
    emails = level.get_emails()
    context_dict = {'alarm' : alarm}
    context_dict['level'] = level
    subject = render_to_string('alarm_message/subject.txt', context_dict)
    subject = ''.join(subject.splitlines())
    message = render_to_string('alarm_message/good_message.html', context_dict)
    send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, emails, fail_silently=False)
    return True


@task
def alert_phones_for_good_performance(alarm, level):
    """
    Sends sms to phones for bad performance.
    """
    phones = level.get_phones()
    # message = ''
    # send_sms(subject, message, settings.DEFAULT_FROM_PHONE, phones, fail_silently=False)
    pass


@task
def check_device_status():
    """
    Will check the status of devices of organizations.
    """
    g_jobs = list()
    ret = False
    service_list = []
    service_data_source_list = []

    #get the device list which is in downtime scheduling today.
    device_id_list = get_today_event_list()['device_ids']
    for org in Organization.objects.all():
        # get the objects which require escalation
        required_objects = EscalationLevel.objects.filter(organization__in=[org])
        if required_objects.exists():
            # if there is actually an escalation object defined
            # if there is none dont worry & return True & relax
            device_type_list = set(required_objects.values_list('device_type__id', flat=True))
            service_list = set(required_objects.values_list('service__name', flat=True))
            service_data_source_list = set(required_objects.values_list('service_data_source__name', flat=True))

            # exclude the devices which is in downtime scheduling today.
            device_list_qs = Device.objects.filter(organization__in=[org],
                                                   device_type__in=device_type_list,
                                                   is_added_to_nms=1
            ).exclude(id__in=device_id_list)

            machine_dict = prepare_machines(device_list_qs)
            for machine_name, device_list in machine_dict.items():
                service_status_list = ServiceStatus.objects.filter(
                    device_name__in=device_list,
                    service_name__in=service_list,
                    data_source__in=service_data_source_list,
                    ip_address__isnull=False
                ).using(alias=machine_name)

                if service_status_list.exists():
                    g_jobs.append(
                        raise_alarms.s(service_status_list=service_status_list,
                                       org=org,
                                       required_levels=required_objects
                        )
                    )

    if not len(g_jobs):
        return ret

    job = group(g_jobs)
    result = job.apply_async()
    # for r in result.get():
    #     ret |= r

    return True


def prepare_machines(device_list_qs):
    """
    Return dict of machine name keys containing values of related devices list.

    :param device_list_qs:
    :return machine_dict:
    """
    unique_device_machine_list = {device.machine.name: True for device in device_list_qs}.keys()

    machine_dict = {}
    for machine in unique_device_machine_list:
        machine_dict[machine] = [device.device_name for device in device_list_qs if device.machine.name == machine]
    return machine_dict


def prepare_services(device_list_qs):
    """
    Return list of services of device types.

    :param device_list_qs:
    :return service_name_list:
    """
    device_type_list = DeviceType.objects.filter(id__in=device_list_qs.values_list('device_type', flat=True))
    return list(DeviceTypeService.objects.filter(
        device_type__in=device_type_list).values_list('service__name', flat=True)
    )


def prepare_service_data_sources(service_name_list):
    """
    Return list of service data sources of services.

    :param service_name_list (List of service names):
    :return data_source_name_list (List of service data sources):
    """
    return list(DeviceTypeServiceDataSource.objects.filter(
        device_type_service__service__name__in=service_name_list).values_list('service_data_sources__name', flat=True)
    )