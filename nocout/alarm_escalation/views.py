from django.views.generic.edit import CreateView, UpdateView, DeleteView, FormView
from django.views.generic import ListView, DetailView, TemplateView, View
from django.core.urlresolvers import reverse_lazy, reverse
import json
from alarm_escalation.models import AlarmEscalation, EscalationLevel, LEVEL_CHOICES
from alarm_escalation.forms import AlarmEscalationForm, EscalationLevelForm
from nocout.mixins.datatable import DatatableOrganizationFilterMixin, DatatableSearchMixin, ValuesQuerySetMixin
from django_datatables_view.base_datatable_view import BaseDatatableView
from nocout.mixins.permissions import PermissionsRequiredMixin


class EscalationList(TemplateView):
    model = AlarmEscalation
    template_name = "alarm_escalation/escalation_list.html"

    def get_context_data(self, **kwargs):
        """
        Preparing the Context Variable required in the template rendering.
        """
        context = super(EscalationList, self).get_context_data(**kwargs)
        datatable_headers = [
            {'mData': 'level', 'sTitle': 'Level', 'sWidth': 'auto', },
            {'mData': 'base_station__alias', 'sTitle': 'BaseStation', 'sWidth': 'auto', 'sClass': 'hidden-xs'},
            {'mData': 'ip', 'sTitle': 'IP Address', 'sWidth': 'auto', },
            #{'mData': 'tilt', 'sTitle': 'Tilt', 'sWidth': 'auto', 'sClass': 'hidden-xs'},
            #{'mData': 'beam_width', 'sTitle': 'Beam Width', 'sWidth': '10%', },
            #{'mData': 'azimuth_angle', 'sTitle': 'Azimuth Angle', 'sWidth': '10%', },
        ]

        #if the user role is Admin or operator or superuser then the action column will appear on the datatable
        user_role = self.request.user.userprofile.role.values_list('role_name', flat=True)
        if 'admin' in user_role or 'operator' in user_role or self.request.user.is_superuser:
            datatable_headers.append({'mData': 'actions', 'sTitle': 'Actions', 'sWidth': '10%', 'bSortable': False})
        context['datatable_headers'] = json.dumps(datatable_headers)
        return context


class EscalationListingTable(PermissionsRequiredMixin,
        DatatableOrganizationFilterMixin,
        DatatableSearchMixin,
        BaseDatatableView,
    ):
    """
    Class based View to render Escalation Data table.
    """
    model = AlarmEscalation
    columns = [ 'technology__alias', 'base_station__alias', 'ip', 'level']
    order_columns = [ 'technology__alias', 'base_station__alias', 'ip', 'level']
    required_permissions = ('alarm_escalation.view_alarmescalation',)

    def prepare_results(self, qs):
        """
        Preparing the final result after fetching from the data base to render on the data table.

        :param qs:
        :return qs

        """
        json_data = [{key: val if val else "" for key, val in dct.items()} for dct in qs]

        for dct in json_data:
            device_id = dct.pop('id')
            if self.request.user.has_perm('alarm_escalation.change_alarmescalation'):
                edit_action = '<a href="/escalation/{0}/edit/"><i class="fa fa-pencil text-dark"></i></a>&nbsp'.format(device_id)
            else:
                edit_action = ''
            if self.request.user.has_perm('alarm_escalation.delete_alarmescalation'):
                delete_action = '<a href="/escalation/{0}/delete/"><i class="fa fa-trash-o text-danger"></i></a>'.format(device_id)
            else:
                delete_action = ''
            if edit_action or delete_action:
                dct.update(actions= edit_action+delete_action)
        return json_data


class AlarmEscalationCreate(PermissionsRequiredMixin, CreateView):
    model = AlarmEscalation
    template_name = "alarm_escalation/escalation_new.html"
    form_class = AlarmEscalationForm
    success_url = reverse_lazy('escalation_list')
    required_permissions = ('alarm_escalation.add_alarmescalation',)


class AlarmEscalationUpdate(PermissionsRequiredMixin, UpdateView):
    model = AlarmEscalation
    template_name = "alarm_escalation/escalation_update.html"
    form_class = AlarmEscalationForm
    success_url = reverse_lazy('escalation_list')
    required_permissions = ('alarm_escalation.change_alarmescalation',)


class AlarmEscalationDelete(PermissionsRequiredMixin, DeleteView):
    model = AlarmEscalation
    template_name = "alarm_escalation/escalation_update.html"
    success_url = reverse_lazy('escalation_list')
    required_permissions = ('alarm_escalation.delete_alarmescalation',)


class LevelList(TemplateView):
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

        #if the user role is Admin or operator or superuser then the action column will appear on the datatable
        user_role = self.request.user.userprofile.role.values_list('role_name', flat=True)
        if 'admin' in user_role or self.request.user.is_superuser:
            datatable_headers.append({'mData': 'actions', 'sTitle': 'Actions', 'sWidth': '10%', 'bSortable': False})
        context['datatable_headers'] = json.dumps(datatable_headers)
        return context


class LevelListingTable(PermissionsRequiredMixin,
        DatatableOrganizationFilterMixin,
        DatatableSearchMixin,
        BaseDatatableView,
    ):
    """
    Class based View to render Escalation Data table.
    """
    model = EscalationLevel
    columns = [ 'name', 'region_name', 'organization__alias', 'emails', 'phones', 'service__alias', 'device_type__alias', 'service_data_source__alias',
                'alarm_age']
    order_columns = [ 'name', 'region_name', 'organization__alias', 'emails', 'phones', 'service__alias', 'device_type__alias', 'service_data_source__alias',
                'alarm_age']
    required_permissions = ('alarm_escalation.view_escalationlevel',)

    def prepare_results(self, qs):
        """
        Preparing the final result after fetching from the data base to render on the data table.

        :param qs:
        :return qs

        """
        level_choices = dict(LEVEL_CHOICES)
        json_data = [{key: val if val else "" for key, val in dct.items()} for dct in qs]
        for dct in json_data:
            device_id = dct.pop('id')
            name = level_choices[dct['name']]
            dct.update(name=name)
            if self.request.user.has_perm('alarm_escalation.change_escalationlevel'):
                edit_action = '<a href="/escalation/level/{0}/edit/"><i class="fa fa-pencil text-dark"></i></a>&nbsp'.format(device_id)
            else:
                edit_action = ''
            if self.request.user.has_perm('alarm_escalation.delete_escalationlevel'):
                delete_action = '<a href="/escalation/level/{0}/delete/"><i class="fa fa-trash-o text-danger"></i></a>'.format(device_id)
            else:
                delete_action = ''
            if edit_action or delete_action:
                dct.update(actions= edit_action+delete_action)
        return json_data


class LevelCreate(PermissionsRequiredMixin, CreateView):
    model = EscalationLevel
    template_name = "level/level_new.html"
    form_class = EscalationLevelForm
    success_url = reverse_lazy('level_list')
    required_permissions = ('alarm_escalation.add_escalationlevel',)


class LevelUpdate(PermissionsRequiredMixin, UpdateView):
    model = EscalationLevel
    template_name = "level/level_update.html"
    form_class = EscalationLevelForm
    success_url = reverse_lazy('level_list')
    required_permissions = ('alarm_escalation.change_escalationlevel',)


class LevelDelete(PermissionsRequiredMixin, DeleteView):
    model = EscalationLevel
    template_name = "level/level_delete.html"
    success_url = reverse_lazy('level_list')
    required_permissions = ('alarm_escalation.delete_escalationlevel',)
