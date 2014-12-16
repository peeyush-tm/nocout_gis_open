"""
Provide celery tasks for Alarm Escalation.
"""

from celery import task
from django.utils import timezone
from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string
from django.shortcuts import render

from organization.models import Organization
from device.models import Device, DeviceType, DeviceTypeService, DeviceTypeServiceDataSource
from performance.models import ServiceStatus
from alarm_escalation.models import EscalationStatus


@task
def raise_alarms(service_status_list, org):
    """
    Raises alarms.
    """
    escalation_level = None
    for service_status in service_status_list:
        if service_status.severity=='ok':
            old_status = 1
            new_status = 1
        else:
            old_status = 0
            new_status = 0
        device = Device.objects.get(device_name=service_status.device_name)
        device_type = DeviceType.objects.get(id=device.device_type)
        obj, created = EscalationStatus.objects.get_or_create(organization=org,
                                            device_type=device_type.name,
                                            service=service_status.service_name,
                                            service_data_source=service_status.data_source,
                                            ip=service_status.ip_address,
                                            defaults={'severity': service_status.severity, 'old_status': old_status, 'new_status': new_status})

        age = timezone.now() - obj.status_since
        level_list = obj.organization.escalationlevel_set.all()
        for level in level_list:
            if age >= level.alarm_age:
                escalation_level = level

        if service_status.severity=='ok':
            obj.new_status = 1
            obj.save()
        else:
            obj.new_status = 0
            obj.save()
        if escalation_level is not None:
            if obj.new_status==0 and obj.old_status==0:
                alert_emails_for_bad_performance.delay(obj, escalation_level)
                alert_phones_for_bad_performance.delay(obj, escalation_level)

            elif obj.new_status==0 and obj.old_status==1:
                obj.old_status = 0
                obj.save()
                alert_emails_for_bad_performance.delay(obj, escalation_level)
                alert_phones_for_bad_performance.delay(obj, escalation_level)

            elif obj.new_status==1 and obj.old_status==0:
                obj.old_status = 1
                obj.save()
                alert_emails_for_good_performance.delay(obj, escalation_level)
                alert_phones_for_good_performance.delay(obj, escalation_level)


# @task
# def raise_alarms_for_bad_performance(service_status_list, org):
#     """
#     Raises alarms for bad performance of device.
#     """
#     escalation_level = None
#     for service_status in service_status_list:
#         device = Device.objects.get(device_name=service_status.device_name)
#         obj, created = EscalationStatus.objects.get_or_create(organization=org,
#                                             device_type=DeviceType.objects.get(id=device.device_type.name),
#                                             service=service_status.service,
#                                             service_data_source=service_status.service_data_source,
#                                             ip=service_status.ip_address,
#                                             severity=service_status.severity)
#         age = timezone.now() - obj.status_since
#         level_list = obj.organization.escalationlevel_set.all()
#         for level in level_list:
#             if age>=level.alarm_age:
#                 escalation_level = level

#         if getattr(obj, 'l%d_email_status' % escalation_level.name) == 0:
#             alert_emails_for_bad_performance.delay(obj, escalation_level)
#             alert_phones_for_bad_performance.delay(obj, escalation_level)
#             setattr(obj, 'l%d_email_status' % escalation_level.name, 1)
#             obj.save()

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


# @task
# def raise_alarms_for_good_performance(service_status_list, org):
#     """
#     Raises alarms for good performance of device.
#     """
#     for service_status in service_status_list:
#         device = Device.objects.get(device_name=service_status.device_name)
#     for escalation in EscalationStatus.objects.get(organization=org,
#                                             device_type=DeviceType.objects.get(id=device.device_type.name),
#                                             service=service_status.service,
#                                             service_data_source=service_status.service_data_source,
#                                             ip=service_status.ip_address,
#                                             severity=service_status.severity)

#     age = timezone.now() - escalation.status_since
#     level_list = EscalationLevel.objects.filter(organization=escalation.organization, alarm_age=age.seconds)

#     for level in level_list:
#         if getattr(escalation, 'l%d_email_status' % level.name) == 1:
#             alert_emails_for_good_performance.delay(escalation, level)
#             alert_phones_for_good_performance.delay(escalation, level)
#             escalation.save()


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
    for org in Organization.objects.all():
        device_list = list(org.device_set.all().values('id', 'machine__name', 'device_name'))
        machine_dict = prepare_machines(device_list)
        service_list = prepare_services(org.device_set.all())
        service_data_source_list = prepare_service_data_sources(service_list)
        for machine_name, device_list in machine_dict.items():
            service_status_list = ServiceStatus.objects.filter(device_name__in=device_list, service_name__in=service_list,
                    data_source__in=service_data_source_list).using(machine_name)
            print service_status_list
            if service_status_list:
                raise_alarms.delay(service_status_list, org)


def prepare_machines(device_values_list_qs):
    """
    Return dict of machine name keys containing values of related devices list.

    :param device_values_list_qs:
    :return machine_dict:
    """
    unique_device_machine_list = {device['machine__name']: True for device in device_values_list_qs}.keys()

    machine_dict = {}
    for machine in unique_device_machine_list:
        machine_dict[machine] = [device['device_name'] for device in device_values_list_qs if device['machine__name'] == machine]
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
