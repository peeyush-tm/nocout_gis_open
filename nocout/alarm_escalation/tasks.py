"""
Provide celery tasks for Alarm Escalation.
"""

from celery import task
from django.utils import timezone
from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string

from alarm_escalation.models import AlarmEscalation
from organization.models import Organization

@task
def raise_alarms_for_bad_performance():
    """
    Raises alarms for bad performance of device.
    """
    for org in Organization.objects.all():
        for alarm in AlarmEscalation.objects.filter(is_closed=False, level__organization=org):
            age = timezone.now() - alarm.status_since
            level = alarm.get_level(age.seconds)

            if getattr(alarm, 'l%d_email_status' % level.name) == 0:
                alert_emails_for_bad_performance.delay(alarm, level)
                alert_phones_for_bad_performance.delay(alarm, level)
                setattr(alarm, 'l%d_email_status' % level.name, 1)
                alarm.save()

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
def raise_alarms_for_good_performance():
    """
    Raises alarms for good performance of device.
    """
    for org in Organization.objects.all():
        for alarm in AlarmEscalation.objects.filter(is_closed=False, level__organization=org):
            age = timezone.now() - alarm.status_since
            level = alarm.get_level(age.seconds)
            if getattr(alarm, 'l%d_email_status' % level.name) == 0:
                alert_emails_for_good_performance.delay(alarm, level)
                alert_phones_for_good_performance.delay(alarm, level)
                alarm.is_closed = True


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

@task
def alert_phones_for_good_performance(alarm, level):
    """
    Sends sms to phones for good performance.
    """
    phones = level.get_phones()
    # message = ''
    # send_sms(subject, message, settings.DEFAULT_FROM_PHONE, phones, fail_silently=False)
    pass

def check_device_status():
    """
    Will check the status of devices of organizations.
    """
    for org in Organization.objects.all():
        devices = org.device_set.all()
        for device in devices:
            machine_name = device.machine.name
