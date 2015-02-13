"""
Provide celery tasks for Alarm Escalation.

    from alarm_escalation.tasks import check_device_status

    check_device_status.delay()
"""

from celery import task
from django.utils import timezone
from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string
from django.shortcuts import render_to_response

from organization.models import Organization
from device.models import Device, DeviceType, DeviceTypeService, DeviceTypeServiceDataSource
from performance.models import ServiceStatus
from alarm_escalation.models import EscalationStatus

from inventory.utils import util as inventory_utils
from scheduling_management.views import get_today_event_list


@task
def raise_alarms(service_status_list, org):
    """
    Raise alarms for bad performance or good performance of device for a particular organization.
    """
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
        # get the DeviceType object of that device.
        device_type = DeviceType.objects.get(id=device.device_type)
        # Get or create the EscalationStatus table for that device, device_type, service(get from service_status) and service_data_source(get from service_status).
        obj, created = EscalationStatus.objects.get_or_create(organization=org,
                device_name=service_status.device_name,
                device_type=device_type.name,
                service=service_status.service_name,
                service_data_source=service_status.data_source,
                defaults={'severity': service_status.severity, 'old_status': old_status, 'new_status': new_status,
                    'status_since': (timezone.now() - timezone.timedelta(seconds=service_status.age)), 'ip': service_status.ip_address,
                }
        )

        # if object is get not created, then update the severity and ip_address of object as per the severity and ip_address of service_status.
        if not created:
            obj.severity = service_status.severity
            obj.ip = service_status.ip_address

        # Get relative levels to inform
        # Get the list of levels of EscalationStatus object after filtering the escalationLevel table on the basis of device_type, service and service_data_source.
        level_list = obj.organization.escalationlevel_set.filter(device_type__name=obj.device_type,
                service__name=obj.service, service_data_source__name=obj.service_data_source)

        # Get current status of device {'good': 1, 'bad': 0}
        # In case of object is not created but get. Update the severity of object as per the severity of service_status.
        if service_status.severity == 'ok':
            obj.new_status = 1
        else:
            obj.new_status = 0

        # Notify for good status of device, if it has started performing good from bad.
        if obj.new_status == 1 and obj.old_status == 0:
            # Update the old_status from 'Bad' to 'Good'.
            obj.old_status = 1
            # Update the status_since.
            obj.status_since = timezone.now() - timezone.timedelta(seconds=service_status.age)

            # Notify to only levels which has been previously notfied for bad status.
            escalation_level_list = []
            for level in level_list:
                # Get the levels from level_list Which has email_status 'Sent', for sending the Good performance message. And Update that level's status to 'Pending'.
                if getattr(obj, 'l%d_email_status' % level.name) == 1:
                    escalation_level_list.append(level)
                    setattr(obj, 'l%d_email_status' % level.name, 0)
                    setattr(obj, 'l%d_phone_status' % level.name, 0)

            # Send the mail and sms for good performance to that level's users.
            alert_emails_for_good_performance.delay(obj, escalation_level_list)
            alert_phones_for_good_performance.delay(obj, escalation_level_list)

        # Notify for bad status of device to level according to alarm age.
        elif obj.new_status == 0:

            # Get level to notify.
            escalation_level = None
            for level in level_list:
                age = timezone.now() - obj.status_since
                # Get the level which should be notified for Bad performance.
                if age.seconds >= level.alarm_age:
                    escalation_level = level

            # Notify only if escalation level has previously not been notified.
            if escalation_level is not None and getattr(obj, 'l%d_email_status' % escalation_level.name) == 0:
                # If old_status was good.
                if obj.old_status == 1:
                    # Update old_status from Good to Bad.
                    obj.old_status = 0
                    # Update status_since.
                    obj.status_since = timezone.now() - timezone.timedelta(seconds=service_status.age)

                # Send email and sms for bad performance.
                alert_emails_for_bad_performance.delay(obj, escalation_level)
                alert_phones_for_bad_performance.delay(obj, escalation_level)
                # Set the email_status and phone_status from "Pending" to "Sent".
                setattr(obj, 'l%d_email_status' % escalation_level.name, 1)
                setattr(obj, 'l%d_phone_status' % escalation_level.name, 1)

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
    message = render_to_string('alarm_message/bad_message.html', context_dict)
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
def alert_emails_for_good_performance(alarm, escalation_level_list):
    """
    Sends Emails for good performance.
    """
    emails = list()
    for level in escalation_level_list:
        emails += (level.get_emails())
    context_dict = {'alarm' : alarm}
    context_dict['level'] = level
    subject = render_to_string('alarm_message/subject.txt', context_dict)
    subject = ''.join(subject.splitlines())
    message = render_to_string('alarm_message/good_message.html', context_dict)
    send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, emails, fail_silently=False)


@task
def alert_phones_for_good_performance(alarm, level_list):
    """
    Sends sms to phones for good performance.
    """
    # phones = level.get_phones()
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

    #get the device list which is in downtime scheduling today.
    device_id_list = get_today_event_list()['device_ids']
    for org in Organization.objects.all():
        machine_dict = prepare_machines(device_list_qs)

        #exclude the devices which is in downtime scheduling today.
        device_list_qs = inventory_utils.organization_network_devices([org]).exclude(id__in=device_id_list)
        service_list = prepare_services(device_list_qs)
        service_data_source_list = prepare_service_data_sources(service_list)
        for machine_name, device_list in machine_dict.items():
            service_status_list = ServiceStatus.objects.filter(device_name__in=device_list, service_name__in=service_list,
                    data_source__in=service_data_source_list, ip_address__isnull=False).using(machine_name)

            if service_status_list:
                raise_alarms.delay(service_status_list, org)


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
