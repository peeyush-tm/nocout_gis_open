"""
Provide celery tasks for Alarm Escalation.
"""

from celery import task
from django.utils import timezone
from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string
from django.shortcuts import render

from alarm_escalation.models import EscalationStatus
from organization.models import Organization
from performance.models import ServiceStatus
from device.models import DeviceType


@task
def raise_alarms_for_bad_performance(service_status_list, org):
    """
    Raises alarms for bad performance of device.
    """
    escalation_level = None
    for service_status in service_status_list:
        device = Device.objects.get(device_name=service_status.device_name)
        obj, created = EscalationStatus.objects.get_or_create(organization=org,
                                            device_type=DeviceType.objects.get(id=device.device_type.name),
                                            service=service_status.service,
                                            service_data_source=service_status.service_data_source,
                                            ip=service_status.ip_address,
                                            severity=service_status.severity)
        age = timezone.now() - obj.status_since
        level_list = obj.organization.escalationlevel_set.all()
        for level in level_list:
            if age>=level.alarm_age:
                escalation_level = level

        if getattr(obj, 'l%d_email_status' % escalation_level.name) == 0:
            alert_emails_for_bad_performance.delay(obj, escalation_level)
            alert_phones_for_bad_performance.delay(obj, escalation_level)
            setattr(obj, 'l%d_email_status' % escalation_level.name, 1)
            obj.save()

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
    message = render('alarm_message/bad_message.html', context_dict)
    send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, emails, fail_silently=False)


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
def raise_alarms_for_good_performance(service_status_list, org):
    """
    Raises alarms for good performance of device.
    """
    for service_status in service_status_list:
        device = Device.objects.get(device_name=service_status.device_name)
    for escalation in EscalationStatus.objects.get(organization=org,
                                            device_type=DeviceType.objects.get(id=device.device_type.name),
                                            service=service_status.service,
                                            service_data_source=service_status.service_data_source,
                                            ip=service_status.ip_address,
                                            severity=service_status.severity)

    age = timezone.now() - escalation.status_since
    level_list = EscalationLevel.objects.filter(organization=escalation.organization, alarm_age=age.seconds)

    for level in level_list:
        if getattr(escalation, 'l%d_email_status' % level.name) == 1:
            alert_emails_for_good_performance.delay(escalation, level)
            alert_phones_for_good_performance.delay(escalation, level)
            escalation.save()


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
    message = render('alarm_message/good_message.html', context_dict)
    send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, emails, fail_silently=False)


@task
def alert_phones_for_good_performance(alarm, level):
    """
    Sends sms to phones for good performance.
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
    service_list = []
    service_data_source_list = []
    severity_list = ['critical', 'warning', 'warn', 'crit']
    service_status_list = []
    for org in Organization.objects.all():
        device_list = org.device_set.all().values('id', 'machine__name', 'device_name')
        machine_dict = prepare_machines(device_list)
        service_list = prepare_services(device_list)
        service_data_source_list = prepare_service_data_sources(service_list)
        for machine_name, device_list in machine_dict.items():
            service_status_list = ServiceStatus.objects.filter(
                                    device_name__in=device_list,
                                    service__in=service_list,
                                    service_data_source__in=service_data_source_list).using(machine_name)
        if service_status_list:
            raise_alarms_for_bad_performance(service_status_list, org)


def prepare_machines(device_list):
    """
    Return dict of machine and device.
    """
    # Unique machine from the device_list
    unique_device_machine_list = {device['machine__name']: True for device in device_list}.keys()

    machine_dict = {}
    #Creating the machine as a key and device_name as a list for that machine.
    for machine in unique_device_machine_list:
        machine_dict[machine] = [device['device_name'] for device in device_list if
                                 device['machine__name'] == machine]

    return machine_dict


def prepare_services(device_list):
    """
    Return list of services of device in device list.
    """
    device_type_list = []
    service_list = []
    for device in device_list:
        device_type_list += DeviceType.objects.filter(id=device.device_type)
    for device_type in device_type_list:
        service_list = device_type.service.all()

    return service_list


def prepare_service_data_sources(service_list):
    """
    Return dict of service data source of device in device list.
    """
    service_data_source_list = []

    for service in service_list:
        service_data_source_list += service.data_source.all()
    return service_data_source_list
