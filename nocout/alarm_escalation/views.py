from django.views.generic.edit import CreateView, UpdateView, DeleteView, FormView
from django.views.generic import ListView, DetailView, TemplateView, View
from django.core.urlresolvers import reverse_lazy, reverse
import json
from alarm_escalation.models import EscalationStatus, EscalationLevel, LEVEL_CHOICES
from alarm_escalation.forms import EscalationLevelForm
from nocout.mixins.datatable import DatatableOrganizationFilterMixin, DatatableSearchMixin, ValuesQuerySetMixin, \
    AdvanceFilteringMixin
from django_datatables_view.base_datatable_view import BaseDatatableView
from nocout.mixins.permissions import PermissionsRequiredMixin
from nocout.mixins.generics import FormRequestMixin
from user_profile.utils.auth import in_group
from alarm_escalation.tasks import mail_send
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
import re
import os.path

import logging

logger = logging.getLogger(__name__)


class LevelList(TemplateView):
    """
    Class Based View for the Escalation data table rendering.
    In this view no data is passed to datatable while rendering template.
    Another ajax call is made to fill in datatable.

    :return:
        context : list of dictionaries in which datatable headers are present for passing them to template.
    """
    model = EscalationLevel
    template_name = "level/level_list.html"

    def get_context_data(self, **kwargs):
        """
        Preparing the Context Variable required in the template rendering.
        """
        context = super(LevelList, self).get_context_data(**kwargs)
        datatable_headers = [
            {'mData': 'organization__alias', 'sTitle': 'Organization', 'sWidth': 'auto', 'sClass': 'hidden-xs'},
            {'mData': 'name', 'sTitle': 'Level', 'sWidth': 'auto', },
            {'mData': 'emails', 'sTitle': 'Email', 'sWidth': 'auto', 'sClass': 'hidden-xs'},
            {'mData': 'phones', 'sTitle': 'SMS', 'sWidth': '10%', },
            {'mData': 'service__alias', 'sTitle': 'Service', 'sWidth': 'auto', },
            {'mData': 'device_type__alias', 'sTitle': 'Device Type', 'sWidth': '10%', },
            {'mData': 'service_data_source__alias', 'sTitle': 'Service Data Source', 'sWidth': '10%', },
            {'mData': 'alarm_age', 'sTitle': 'Escalation Age', 'sWidth': '10%', },
        ]

        # if the user role is Admin or operator or superuser then the action column will appear on the datatable
        if in_group(self.request.user, 'admin'):
            datatable_headers.append({'mData': 'actions', 'sTitle': 'Actions', 'sWidth': '10%', 'bSortable': False})
        context['datatable_headers'] = json.dumps(datatable_headers)
        return context


class LevelListingTable(PermissionsRequiredMixin,
                        DatatableOrganizationFilterMixin,
                        DatatableSearchMixin,
                        BaseDatatableView,
                        AdvanceFilteringMixin
                        ):
    """
    Class based View to render Escalation Level Data table.
    """

    model = EscalationLevel
    columns = ['name', 'region_name', 'organization__alias', 'emails', 'phones', 'service__alias', 'device_type__alias',
               'service_data_source__alias',
               'alarm_age']
    order_columns = ['organization__alias', 'name', 'emails', 'phones', 'service__alias', 'device_type__alias',
                     'service_data_source__alias',
                     'alarm_age']
    required_permissions = ('alarm_escalation.view_escalationlevel',)

    def prepare_results(self, qs):
        """
        Preparing the final result after fetching from the data base to render on the data table.

        :Args:
            qs : QuerySet object

        :return:
            json_data : list of dictionaries 
        """
        level_choices = dict(LEVEL_CHOICES)
        json_data = [{key: val if val else "" for key, val in dct.items()} for dct in qs]
        for dct in json_data:
            device_id = dct.pop('id')
            name = level_choices[dct['name']]
            dct.update(name=name)
            if self.request.user.has_perm('alarm_escalation.change_escalationlevel'):
                edit_action = '<a href="/escalation/level/{0}/edit/"><i class="fa fa-pencil text-dark"></i></a>&nbsp'.format(
                    device_id)
            else:
                edit_action = ''
            if self.request.user.has_perm('alarm_escalation.delete_escalationlevel'):
                delete_action = '<a href="/escalation/level/{0}/delete/"><i class="fa fa-trash-o text-danger"></i></a>'.format(
                    device_id)
            else:
                delete_action = ''
            if edit_action or delete_action:
                dct.update(actions=edit_action + delete_action)
        return json_data


class LevelCreate(PermissionsRequiredMixin, FormRequestMixin, CreateView):
    """
    Class based view to create new Escalation Level.
    """
    model = EscalationLevel
    template_name = "level/level_new.html"
    form_class = EscalationLevelForm
    success_url = reverse_lazy('level_list')
    required_permissions = ('alarm_escalation.add_escalationlevel',)


class LevelUpdate(PermissionsRequiredMixin, FormRequestMixin, UpdateView):
    """
    Class based view to update Escalation Level
    """
    model = EscalationLevel
    template_name = "level/level_update.html"
    form_class = EscalationLevelForm
    success_url = reverse_lazy('level_list')
    required_permissions = ('alarm_escalation.change_escalationlevel',)


class LevelDelete(PermissionsRequiredMixin, DeleteView):
    """
    Class based view to Delete Escalation Level.
    """
    model = EscalationLevel
    template_name = "level/level_delete.html"
    success_url = reverse_lazy('level_list')
    required_permissions = ('alarm_escalation.delete_escalationlevel',)


class EmailSender(View):
    """
    Send email to multiple mail id's with multiple attachment.

    URL: http://127.0.0.1:8000/articles/email/

    Args:
        subject (unicode): Mail subject.
        message (unicode): Email Message will be here.
        from_email (unicode): Sender's email.
        to_email (list): List of email id where to send mail.
        attachments (list): Mail attachments if any(file object).
        success (int) : Success bit either 0/1.
        error_message (string): String containing error messages.
        attachment_path (list) : List of File path.

    Return (dict): Response to be returnes in json format.
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

    @csrf_exempt
    def dispatch(self, *args, **kwargs):
        return super(EmailSender, self).dispatch(*args, **kwargs)

    def post(self, request, *args, **kwargs):
        # From email id.
        from_email = self.request.POST.get('from_email', None)
        # To email id.
        to_email = self.request.POST.get('to_email')
        # If multiple values then by using eval converting into list.
        logger.exception('################type of to_email------', type(to_email))
        to_email = str(to_email)  # Parsing to string.
        if to_email:
            if "," in to_email:
                to_email = eval(to_email)
            elif type(to_email) == str:
                to_email = to_email.split(",")
        # Subject.
        subject = self.request.POST.get('subject', None)
        # Message.
        message = self.request.POST.get('message', None)
        # Path of File attachments.
        attachment_path = self.request.POST.get('attachment_path')

        if attachment_path:
            if "," in attachment_path:
                attachment_path = eval(attachment_path)
            elif type(attachment_path) == str:
                    attachment_path = attachment_path.split(",")

        attachments = None
        try:
            attachments = self.request.FILES.values()
        except Exception as e:
            logger.exception(e.message)

        # Result: Response to be returned.
        result = {
            "success": 0,
            "message": "Failed to send email.",

            "data": {
                "subject": subject,
                "message": message,
                "from_email": from_email,
                "to_email": to_email,
                "attachments": attachments,
                "attachment_path": attachment_path,
            }
        }

        # Expected errors has been stored here.
        error_messages = ""

        # Field validations.
        if not to_email:
            # 'error_message' generation when 'to_email' value not provided.
            error_messages += "Please specify email id of sender. \n"

        if not from_email:
            result['from_email'] = settings.DEFAULT_FROM_EMAIL

        if attachment_path:
            for x in attachment_path:
                # Avoiding if it is URL Path.
                if re.search('^http.*', x):
                    pass
                else:
                    # If file exist in system
                    if not os.path.isfile(x):
                        error_messages = "file: '%s' doesn't exist \n" % x
        else:
            result['data']['attachment_path'] = []

        if error_messages:
            result['message'] = error_messages
            # return HttpResponse(json.dumps(result))
        else:
            result['success'] = 1
            result['message'] = "Successfully send the email."
            # Sending email as a backend task.
            mail_send.delay(result)
        if result['data']['attachments']:
            attachments_name = [x.name for x in result['data']['attachments']]
            result['data']['attachments'] = attachments_name

        return HttpResponse(json.dumps(result))
