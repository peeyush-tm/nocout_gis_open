import json
from django.db.models.query import ValuesQuerySet
from django.http import HttpResponseRedirect
from django.views.generic import ListView, DetailView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.core.urlresolvers import reverse_lazy
from django_datatables_view.base_datatable_view import BaseDatatableView
from models import Service, ServiceParameters, ServiceDataSource, Protocol, DeviceServiceConfiguration
from .forms import ServiceForm, ServiceParametersForm, ServiceDataSourceForm, ProtocolForm
from nocout.utils.util import DictDiffer
from django.db.models import Q
from nocout.mixins.user_action import UserLogDeleteMixin
from nocout.mixins.permissions import PermissionsRequiredMixin
from nocout.mixins.datatable import DatatableSearchMixin, ValuesQuerySetMixin
from service.forms import ServiceDataSourceCreateFormSet, ServiceDataSourceUpdateFormSet

# ########################################################
from django.conf import settings

if settings.DEBUG:
    import logging

    logger = logging.getLogger(__name__)
#########################################################


# **************************************** Service *********************************************
class ServiceList(PermissionsRequiredMixin, ListView):
    """
    Class Based to render the Service Listing page.
    """
    model = Service
    template_name = 'service/services_list.html'
    required_permissions = ('service.view_service',)

    def get_context_data(self, **kwargs):
        """
        Preparing the Context Variable required in the template rendering.
        """
        context = super(ServiceList, self).get_context_data(**kwargs)
        datatable_headers = [
            {'mData': 'name', 'sTitle': 'Name', 'sWidth': 'auto', },
            {'mData': 'alias', 'sTitle': 'Alias', 'sWidth': 'auto', 'sClass': 'hidden-xs'},
            {'mData': 'parameters__parameter_description', 'sTitle': 'Default Parameters', 'sWidth': 'auto', },
            {'mData': 'service_data_sources__alias', 'sTitle': 'Data Sources', 'sWidth': 'auto', },
            {'mData': 'description', 'sTitle': 'Description', 'sWidth': 'auto', 'sClass': 'hidden-xs'},
        ]
        if 'admin' in self.request.user.userprofile.role.values_list('role_name', flat=True):
            datatable_headers.append({'mData':'actions', 'sTitle':'Actions', 'sWidth':'5%', 'bSortable': False})
        context['datatable_headers'] = json.dumps(datatable_headers)
        return context


class ServiceListingTable(PermissionsRequiredMixin, DatatableSearchMixin, BaseDatatableView):
    """
    Class based View to render Service Listing Table.
    """
    model = Service
    required_permissions = ('service.view_service',)
    columns = ['name', 'alias', 'parameters__parameter_description', 'service_data_sources__alias', 'description']
    order_columns = ['name', 'alias', 'parameters__parameter_description','service_data_sources__alias', 'description']

    def get_initial_queryset(self):
        if not self.model:
            raise NotImplementedError("Need to provide a model or implement get_initial_queryset!")
        qs = self.model.objects.filter()
        return qs.prefetch_related('service_data_sources')

    def prepare_results(self, qs):
        """
        Preparing the final result after fetching from the data base to render on the data table.

        :param qs:
        :return qs

        """
        json_data = []
        for obj in qs:
            dct = {}
            dct.update(name=obj.name)
            dct.update(alias=obj.alias)
            dct.update(parameters__parameter_description=obj.parameters.parameter_description)
            dct.update(description=obj.description)
            dct.update(service_data_sources__alias=', '.join(list(obj.service_data_sources.values_list('alias', flat=True))))
            dct.update(actions='<a href="/service/{0}/edit/"><i class="fa fa-pencil text-dark"></i></a>\
                <a href="/service/{0}/delete/"><i class="fa fa-trash-o text-danger"></i></a>'.format(obj.id))
            json_data.append(dct)
        return json_data


class ServiceDetail(PermissionsRequiredMixin, DetailView):
    """
    Class Based View to render the Service Details

    """
    model = Service
    required_permissions = ('service.view_service',)
    template_name = 'service/service_detail.html'


class ServiceCreate(PermissionsRequiredMixin, CreateView):
    """
    Class Based View to Create the Service
    """
    template_name = 'service/service_new.html'
    model = Service
    form_class = ServiceForm
    success_url = reverse_lazy('services_list')
    required_permissions = ('service.add_service',)

    def get(self, request, *args, **kwargs):
        """
        Handles GET requests and instantiates blank versions of the form
        and its inline formsets.
        """
        self.object = None
        form_class = self.get_form_class()
        form = self.get_form(form_class)
        Service_data_form = ServiceDataSourceCreateFormSet()
        return self.render_to_response(
            self.get_context_data(form=form,
                                  service_data_form=Service_data_form))

    def post(self, request, *args, **kwargs):
        """
        Handles POST requests, instantiating a form instance and its inline
        formsets with the passed POST variables and then checking them for
        validity.
        """
        self.object = None
        form_class = self.get_form_class()
        form = self.get_form(form_class)
        service_data_form = ServiceDataSourceCreateFormSet(self.request.POST)
        if (form.is_valid() and service_data_form.is_valid()):
            return self.form_valid(form, service_data_form)
        else:
            return self.form_invalid(form, service_data_form)

    def form_valid(self, form, service_data_form):
        """
        Called if all forms are valid. Creates a Recipe instance along with
        associated Ingredients and Instructions and then redirects to a
        success page.
        """
        self.object = form.save()
        service_data_form.instance = self.object
        service_data_form.save()
        return HttpResponseRedirect(self.get_success_url())

    def form_invalid(self, form, service_data_form):
        """
        Called if a form is invalid. Re-renders the context data with the
        data-filled forms and errors.
        """
        return self.render_to_response(
            self.get_context_data(form=form,
                                  service_data_form=service_data_form))


class ServiceUpdate(PermissionsRequiredMixin, UpdateView):
    """
    Class Based View to update the Service.
    """
    template_name = 'service/service_update.html'
    model = Service
    form_class = ServiceForm
    success_url = reverse_lazy('services_list')
    required_permissions = ('service.change_service',)

    def get(self, request, *args, **kwargs):
        """
        Handles GET requests and instantiates blank versions of the form
        and its inline formsets.
        """
        self.object = self.get_object()
        form_class = self.get_form_class()
        form = ServiceForm(instance=self.object)
        Service_data_form = ServiceDataSourceUpdateFormSet(instance=self.object)
        if len(Service_data_form):
            Service_data_form = ServiceDataSourceUpdateFormSet(instance=self.object)
        else:
            Service_data_form = ServiceDataSourceCreateFormSet()
        return self.render_to_response(
            self.get_context_data(form=form,
                                  service_data_form=Service_data_form))

    def post(self, request, *args, **kwargs):
        """
        Handles POST requests, instantiating a form instance and its inline
        formsets with the passed POST variables and then checking them for
        validity.
        """
        self.object = self.get_object()
        form_class = self.get_form_class()
        form = self.get_form(form_class)
        service_data_form = ServiceDataSourceUpdateFormSet(self.request.POST, instance=self.object)
        if (form.is_valid() and service_data_form.is_valid()):
            return self.form_valid(form, service_data_form)
        else:
            return self.form_invalid(form, service_data_form)

    def form_valid(self, form, service_data_form):
        """
        Called if all forms are valid. Creates a Recipe instance along with
        associated Ingredients and Instructions and then redirects to a
        success page.
        """
        self.object = form.save()
        service_data_form.instance = self.object
        service_data_form.save()
        return HttpResponseRedirect(self.get_success_url())

    def form_invalid(self, form, service_data_form):
        """
        Called if a form is invalid. Re-renders the context data with the
        data-filled forms and errors.
        """
        return self.render_to_response(
            self.get_context_data(form=form,
                                  service_data_form=service_data_form))


class ServiceDelete(PermissionsRequiredMixin, UserLogDeleteMixin, DeleteView):
    """
    Class Based View to Delete the Service.
    """
    model = Service
    template_name = 'service/service_delete.html'
    success_url = reverse_lazy('services_list')
    required_permissions = ('service.delete_service',)


#************************************* Service Parameters *****************************************
class ServiceParametersList(PermissionsRequiredMixin, ListView):
    """
    Class Based View for the Service parameter Listing.
    """
    model = ServiceParameters
    template_name = 'service_parameter/services_parameter_list.html'
    required_permissions = ('service.view_serviceparameters',)

    def get_context_data(self, **kwargs):
        """
        Preparing the Context Variable required in the template rendering.
        """
        context = super(ServiceParametersList, self).get_context_data(**kwargs)
        datatable_headers = [
            {'mData': 'parameter_description', 'sTitle': 'Parameter Description', 'sWidth': 'auto', },
            {'mData': 'protocol__name', 'sTitle': 'Protocol', 'sWidth': 'auto', },
            {'mData': 'normal_check_interval', 'sTitle': 'Normal Check Intervals', 'sWidth': 'auto',
             'sClass': 'hidden-xs'},
            {'mData': 'retry_check_interval', 'sTitle': 'Retry Check Intervals', 'sWidth': 'auto', },
            {'mData': 'max_check_attempts', 'sTitle': 'Max Check Attempts', 'sWidth': 'auto', },
        ]
        if 'admin' in self.request.user.userprofile.role.values_list('role_name', flat=True):
            datatable_headers.append({'mData':'actions', 'sTitle':'Actions', 'sWidth':'5%', 'bSortable': False})
        context['datatable_headers'] = json.dumps(datatable_headers)
        return context


class ServiceParametersListingTable(PermissionsRequiredMixin, DatatableSearchMixin, ValuesQuerySetMixin, BaseDatatableView):
    """
    Class based View to render ServiceParameters Data table.
    """
    model = ServiceParameters
    required_permissions = ('service.view_serviceparameters',)
    columns = ['parameter_description', 'protocol__name', 'normal_check_interval', 'retry_check_interval',
               'max_check_attempts']
    order_columns = ['parameter_description', 'protocol__name', 'normal_check_interval', 'retry_check_interval',
                     'max_check_attempts']

    def prepare_results(self, qs):
        """
        Preparing the final result after fetching from the data base to render on the data table.

        :param qs:
        :return qs

        """
        json_data = [{key: val if val else "" for key, val in dct.items()} for dct in qs]
        for dct in json_data:
            dct.update(actions='<a href="/service_parameter/{0}/edit/"><i class="fa fa-pencil text-dark"></i></a>\
                <a href="/service_parameter/{0}/delete/"><i class="fa fa-trash-o text-danger"></i></a>'.format(
                dct.pop('id')))
        return json_data


class ServiceParametersDetail(PermissionsRequiredMixin, DetailView):
    """
    Class Based View to render the details of the service parameters
    """
    model = ServiceParameters
    required_permissions = ('service.view_serviceparameters',)
    template_name = 'service_parameter/service_parameter_detail.html'


class ServiceParametersCreate(PermissionsRequiredMixin, CreateView):
    """
    Class based View to create the service parameters
    """
    template_name = 'service_parameter/service_parameter_new.html'
    model = ServiceParameters
    form_class = ServiceParametersForm
    success_url = reverse_lazy('services_parameter_list')
    required_permissions = ('service.add_serviceparameters',)


class ServiceParametersUpdate(PermissionsRequiredMixin, UpdateView):
    """
    Class Based View to Update the Service Parameters.
    """
    template_name = 'service_parameter/service_parameter_update.html'
    model = ServiceParameters
    form_class = ServiceParametersForm
    success_url = reverse_lazy('services_parameter_list')
    required_permissions = ('service.change_serviceparameters',)


class ServiceParametersDelete(PermissionsRequiredMixin, UserLogDeleteMixin, DeleteView):
    """
    Class Based View to Delete the ServiceParameters.
    """
    model = ServiceParameters
    template_name = 'service_parameter/service_parameter_delete.html'
    success_url = reverse_lazy('services_parameter_list')
    required_permissions = ('service.delete_serviceparameters',)
    obj_alias = 'parameter_description'


#********************************** Service Data Source ***************************************
class ServiceDataSourceList(PermissionsRequiredMixin, ListView):
    """
    Class Based View to render the Service Data Source.
    """
    model = ServiceDataSource
    template_name = 'service_data_source/service_data_sources_list.html'
    required_permissions = ('service.view_servicedatasource',)

    def get_context_data(self, **kwargs):
        """
        Preparing the Context Variable required in the template rendering.
        """
        context = super(ServiceDataSourceList, self).get_context_data(**kwargs)
        datatable_headers = [
            {'mData': 'name', 'sTitle': 'Name', 'sWidth': 'auto', },
            {'mData': 'alias', 'sTitle': 'Alias', 'sWidth': 'auto', 'sClass': 'hidden-xs'},
            {'mData': 'warning', 'sTitle': 'Warning', 'sWidth': 'auto', },
            {'mData': 'critical', 'sTitle': 'Critical', 'sWidth': 'auto', 'sClass': 'hidden-xs'},
        ]
        if 'admin' in self.request.user.userprofile.role.values_list('role_name', flat=True):
            datatable_headers.append({'mData':'actions', 'sTitle':'Actions', 'sWidth':'5%', 'bSortable': False})

        context['datatable_headers'] = json.dumps(datatable_headers)
        return context


class ServiceDataSourceListingTable(PermissionsRequiredMixin, ValuesQuerySetMixin, DatatableSearchMixin, BaseDatatableView):
    model = ServiceDataSource
    required_permissions = ('service.view_servicedatasource',)
    columns = ['name', 'alias', 'warning', 'critical']
    order_columns = ['name', 'alias', 'warning', 'critical']

    def prepare_results(self, qs):
        """
        Preparing the final result after fetching from the data base to render on the data table.

        :param qs:
        :return qs

        """

        json_data = [{key: val if val else "" for key, val in dct.items()} for dct in qs]
        for dct in json_data:
            dct.update(actions='<a href="/service_data_source/{0}/edit/"><i class="fa fa-pencil text-dark"></i></a>\
                <a href="/service_data_source/{0}/delete/"><i class="fa fa-trash-o text-danger"></i></a>'.format(
                dct.pop('id')))
        return json_data


class ServiceDataSourceDetail(PermissionsRequiredMixin, DetailView):
    """
    Class Based View to render the Service Data Source Detail information.
    """
    model = ServiceDataSource
    required_permissions = ('service.view_servicedatasource',)
    template_name = 'service_data_source/service_data_source_detail.html'


class ServiceDataSourceCreate(PermissionsRequiredMixin, CreateView):
    """
    Class Based View to Creater the Service Data Source Detail.
    """
    template_name = 'service_data_source/service_data_source_new.html'
    model = ServiceDataSource
    form_class = ServiceDataSourceForm
    success_url = reverse_lazy('service_data_sources_list')
    required_permissions = ('service.add_servicedatasource',)


class ServiceDataSourceUpdate(PermissionsRequiredMixin, UpdateView):
    """
    Class based View to update the Service Data Source.
    """
    template_name = 'service_data_source/service_data_source_update.html'
    model = ServiceDataSource
    form_class = ServiceDataSourceForm
    success_url = reverse_lazy('service_data_sources_list')
    required_permissions = ('service.change_servicedatasource',)


class ServiceDataSourceDelete(PermissionsRequiredMixin, UserLogDeleteMixin, DeleteView):
    """
    Class Based View to Delete the Service Data Source.
    """
    model = ServiceDataSource
    template_name = 'service_data_source/service_data_source_delete.html'
    success_url = reverse_lazy('service_data_sources_list')
    required_permissions = ('service.delete_servicedatasource',)


#********************************** Protocol ***************************************
class ProtocolList(PermissionsRequiredMixin, ListView):
    """
    Class Based View to render the List page.
    """
    model = Protocol
    template_name = 'protocol/protocols_list.html'
    required_permissions = ('service.view_protocol',)

    def get_context_data(self, **kwargs):
        """
        Preparing the Context Variable required in the template rendering.
        """
        context = super(ProtocolList, self).get_context_data(**kwargs)
        datatable_headers = [
            {'mData': 'name', 'sTitle': 'Name', 'sWidth': 'auto', },
            {'mData': 'protocol_name', 'sTitle': 'Protocol Name', 'sWidth': 'auto', 'sClass': 'hidden-xs'},
            {'mData': 'port', 'sTitle': 'Port', 'sWidth': 'auto', },
            {'mData': 'version', 'sTitle': 'Version', 'sWidth': 'auto', 'sClass': 'hidden-xs'},
            {'mData': 'read_community', 'sTitle': 'Read Community', 'sWidth': 'auto', },
            {'mData': 'write_community', 'sTitle': 'Write Community', 'sWidth': 'auto', 'sClass': 'hidden-xs'},
            {'mData': 'auth_password', 'sTitle': 'Auth Password', 'sWidth': 'auto', },
            {'mData': 'auth_protocol', 'sTitle': 'Auth Protocol', 'sWidth': 'auto', 'sClass': 'hidden-xs'},
            {'mData': 'security_name', 'sTitle': 'Security Name', 'sWidth': 'auto', },
            {'mData': 'security_level', 'sTitle': 'Security Level', 'sWidth': 'auto', 'sClass': 'hidden-xs'},
            {'mData': 'private_phase', 'sTitle': 'Private Phase', 'sWidth': 'auto', },
            {'mData': 'private_pass_phase', 'sTitle': 'Private Pass Phase', 'sWidth': 'auto', 'sClass': 'hidden-xs'},
        ]
        if 'admin' in self.request.user.userprofile.role.values_list('role_name', flat=True):
            datatable_headers.append({'mData':'actions', 'sTitle':'Actions', 'sWidth':'5%', 'bSortable': False})
        context['datatable_headers'] = json.dumps(datatable_headers)
        return context


class ProtocolListingTable(PermissionsRequiredMixin, ValuesQuerySetMixin, DatatableSearchMixin, BaseDatatableView):
    """
    Class Based View to render the protocol Data table.
    """
    model = Protocol
    required_permissions = ('service.view_protocol',)
    columns = ['name', 'protocol_name', 'port', 'version', 'read_community', 'write_community', 'auth_password',
               'auth_protocol', 'security_name', 'security_level', 'private_phase', 'private_pass_phase']
    order_columns = ['name', 'protocol_name', 'port', 'version', 'read_community', 'write_community', 'auth_password',
                     'auth_protocol', 'security_name', 'security_level', 'private_phase', 'private_pass_phase']

    def prepare_results(self, qs):
        """
        Preparing the final result after fetching from the data base to render on the data table.

        :param qs:
        :return qs
        """

        json_data = [{key: val if val else "" for key, val in dct.items()} for dct in qs]
        for dct in json_data:
            dct.update(actions='<a href="/protocol/{0}/edit/"><i class="fa fa-pencil text-dark"></i></a>\
                <a href="/protocol/{0}/delete/"><i class="fa fa-trash-o text-danger"></i></a>'.format(dct.pop('id')))
        return json_data


class ProtocolDetail(PermissionsRequiredMixin, DetailView):
    """
    Class Based View to render the detail Protocol information
    """
    model = Protocol
    required_permissions = ('service.view_protocol',)
    template_name = 'protocol/protocol_detail.html'


class ProtocolCreate(PermissionsRequiredMixin, CreateView):
    """
    Class based View to Create the Protocol.
    """
    template_name = 'protocol/protocol_new.html'
    model = Protocol
    form_class = ProtocolForm
    success_url = reverse_lazy('protocols_list')
    required_permissions = ('service.add_protocol',)


class ProtocolUpdate(PermissionsRequiredMixin, UpdateView):
    """
    Class Based View to update the protocol.
    """
    template_name = 'protocol/protocol_update.html'
    model = Protocol
    form_class = ProtocolForm
    success_url = reverse_lazy('protocols_list')
    required_permissions = ('service.change_protocol',)


class ProtocolDelete(PermissionsRequiredMixin, UserLogDeleteMixin, DeleteView):
    """
    Class Based View to delete the protocol.
    """
    model = Protocol
    template_name = 'protocol/protocol_delete.html'
    success_url = reverse_lazy('protocols_list')
    required_permissions = ('service.delete_protocol',)
    obj_alias = 'protocol_name'


#**************************************** DeviceServiceConfiguration *********************************************
class DeviceServiceConfigurationList(PermissionsRequiredMixin, ListView):
    """
    Class Based View to list the Device Service Configuration page.
    """
    model = DeviceServiceConfiguration
    template_name = 'device_service_configuration/device_service_configuration_list.html'
    required_permissions = ('service.view_deviceserviceconfiguration',)

    def get_context_data(self, **kwargs):
        """
        Preparing the Context Variable required in the template rendering.
        """
        context=super(DeviceServiceConfigurationList, self).get_context_data(**kwargs)
        datatable_headers = [
            {'mData':'device_name',             'sTitle' : 'Device',                'sWidth':'null',},
            {'mData':'service_name',            'sTitle' : 'Service',               'sWidth':'null',},
            {'mData':'agent_tag',               'sTitle' : 'Agent Tag',             'sWidth':'null',},
            {'mData':'port',                    'sTitle' : 'Port',                  'sWidth':'null',},
            {'mData':'version',                 'sTitle' : 'Version',               'sWidth':'null',},
            {'mData':'read_community',          'sTitle' : 'Read Community',        'sWidth':'null',},
            {'mData':'svc_template',            'sTitle' : 'Template',              'sWidth':'null',},
            {'mData':'normal_check_interval',   'sTitle' : 'Normal CI',             'sWidth':'null',},
            {'mData':'retry_check_interval',    'sTitle' : 'Retry CI',              'sWidth':'null',},
            {'mData':'max_check_attempts',      'sTitle' : 'Max Attempts',          'sWidth':'null',},
            {'mData':'data_source',             'sTitle' : 'DS',                    'sWidth':'null',},
            {'mData':'warning',                 'sTitle' : 'Warning',               'sWidth':'null',},
            {'mData':'critical',                'sTitle' : 'Critical',              'sWidth':'null',},
            {'mData':'added_on',                'sTitle' : 'Added On',              'sWidth':'null',},
            {'mData':'modified_on',             'sTitle' : 'Updated On',            'sWidth':'null',},
        ]

        if 'admin' in self.request.user.userprofile.role.values_list('role_name', flat=True):
            datatable_headers.append({'mData':'actions', 'sTitle':'Actions', 'sWidth':'5%', 'bSortable': False})

        context['datatable_headers'] = json.dumps(datatable_headers)
        return context

class DeviceServiceConfigurationListingTable(PermissionsRequiredMixin, DatatableSearchMixin, ValuesQuerySetMixin, BaseDatatableView):
    """
    Class based View render the Device Service Configuration Table.
    """
    model = DeviceServiceConfiguration
    required_permissions = ('service.view_deviceserviceconfiguration',)
    columns = ['device_name', 'service_name', 'agent_tag', 'port', 'version','read_community', 'svc_template',
               'normal_check_interval', 'retry_check_interval', 'max_check_attempts', 'data_source', 'warning', \
               'critical', 'added_on', 'modified_on']
    order_columns = ['device_name', 'service_name', 'agent_tag', 'port', 'version','read_community', 'svc_template',
                     'normal_check_interval', 'retry_check_interval', 'max_check_attempts', 'data_source', 'warning', \
                     'critical', 'added_on', 'modified_on']
    search_columns = ['device_name', 'service_name', 'agent_tag', 'port', 'version','read_community', 'svc_template',
               'normal_check_interval', 'retry_check_interval', 'max_check_attempts', 'data_source', 'warning', \
               'critical']

    def prepare_results(self, qs):
        """
        Preparing the final result after fetching from the data base to render on the data table.

        :param qs:
        :return qs
        """


        json_data = [ { key: val if val else "" for key, val in dct.items() } for dct in qs ]
        for dct in json_data:
            dct.update(actions='<a href="#" onclick="Dajaxice.device.edit_single_service_form(get_single_service_edit_form,\
                               {{\'dsc_id\': {0}}})"><i class="fa fa-pencil text-dark"></i></a>\
                                <a href="#" onclick="Dajaxice.device.delete_single_service_form(get_single_service_delete_form,\
                                {{\'dsc_id\': {0}}})"><i class="fa fa-trash-o text-danger"></i></a>'.format(dct.pop('id')),
                       added_on=dct['added_on'].strftime("%Y-%m-%d %H:%M:%S"),
                       modified_on=dct['modified_on'].strftime("%Y-%m-%d %H:%M:%S"))

        return json_data
