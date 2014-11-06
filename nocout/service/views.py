import json
from django.contrib.auth.decorators import permission_required
from django.db.models.query import ValuesQuerySet
from django.http import HttpResponseRedirect
from django.utils.decorators import method_decorator
from django.views.generic import ListView, DetailView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.core.urlresolvers import reverse_lazy
from django_datatables_view.base_datatable_view import BaseDatatableView
from models import Service, ServiceParameters, ServiceDataSource, Protocol, DeviceServiceConfiguration
from .forms import ServiceForm, ServiceParametersForm, ServiceDataSourceForm, ProtocolForm
from nocout.utils.util import DictDiffer
from django.db.models import Q
from activity_stream.models import UserAction
from nocout.mixins.permissions import PermissionsRequiredMixin

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


class ServiceListingTable(PermissionsRequiredMixin, BaseDatatableView):
    """
    Class based View to render Service Listing Table.
    """
    model = Service
    required_permissions = ('service.view_service',)
    columns = ['name', 'alias', 'parameters__parameter_description', 'service_data_sources__alias', 'description']
    order_columns = ['name', 'alias', 'parameters__parameter_description','service_data_sources__alias', 'description']

    def filter_queryset(self, qs):
        """
        The filtering of the queryset with respect to the search keyword entered.

        :param qs:
        :return qs:
        """
        sSearch = self.request.GET.get('sSearch', None)
        if sSearch:
            query = []
            exec_query = "qs = %s.objects.filter(" % (self.model.__name__)
            for column in self.columns:
                query.append("Q(%s__icontains=" % column + "\"" + sSearch + "\"" + ")")

            exec_query += " | ".join(query)
            exec_query += ").values(*" + str(self.columns + ['id']) + ")"
            exec exec_query

        return qs

    def get_initial_queryset(self):
        """
        Preparing  Initial Queryset for the for rendering the data table.
        """
        if not self.model:
            raise NotImplementedError("Need to provide a model or implement get_initial_queryset!")
        return Service.objects.values(*self.columns + ['id'])

    def prepare_results(self, qs):
        """
        Preparing the final result after fetching from the data base to render on the data table.

        :param qs:
        :return qs

        """
        if qs:
            qs = [{key: val if val else "" for key, val in dct.items()} for dct in qs]

        #in correct behaviour on GUI. need to be redone. @TODO
        # ##joining the multiple data sources in one
        # new_qs = []
        # temp_dict = {}
        # delete_list = []
        # for ds in qs:
        #     if ds["id"] not in temp_dict:
        #         temp_dict[ds["id"]] = []
        #     temp_dict[ds["id"]].append(ds["service_data_sources__alias"])
        #
        # for q in qs:
        #     if q["id"] not in delete_list:
        #         delete_list.append(q["id"])
        #         for sid in temp_dict:
        #             if sid == q["id"]:
        #                 q["service_data_sources__alias"] = ", ".join(temp_dict[sid])
        #                 new_qs.append(q)
        # ##joining the multiple data sources in one.
        # ## replacing old one
        # qs = new_qs
        # ## replacing old one

        for dct in qs:
            dct.update(actions='<a href="/service/edit/{0}"><i class="fa fa-pencil text-dark"></i></a>\
                <a href="/service/delete/{0}"><i class="fa fa-trash-o text-danger"></i></a>'.format(dct.pop('id')))
        return qs

    def get_context_data(self, *args, **kwargs):
        """
        The main function call to fetch, search, ordering , prepare and display the data on the data table.
        """
        request = self.request
        self.initialize(*args, **kwargs)

        qs = self.get_initial_queryset()

        # number of records before filtering
        total_records = qs.count()

        qs = self.filter_queryset(qs)

        # number of records after filtering
        total_display_records = qs.count()

        qs = self.ordering(qs)
        qs = self.paging(qs)
        #if the qs is empty then JSON is unable to serialize the empty ValuesQuerySet.Therefore changing its type to list.
        if not qs and isinstance(qs, ValuesQuerySet):
            qs = list(qs)

        # prepare output data
        aaData = self.prepare_results(qs)
        ret = {'sEcho': int(request.REQUEST.get('sEcho', 0)),
               'iTotalRecords': total_records,
               'iTotalDisplayRecords': total_display_records,
               'aaData': aaData
        }
        return ret


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

    def form_valid(self, form):
        """
        Submit the form and log the user activity.
        """
        self.object = form.save()
        return HttpResponseRedirect(ServiceCreate.success_url)


class ServiceUpdate(PermissionsRequiredMixin, UpdateView):
    """
    Class Based View to update the Service.
    """
    template_name = 'service/service_update.html'
    model = Service
    form_class = ServiceForm
    success_url = reverse_lazy('services_list')
    required_permissions = ('service.change_service',)

    def form_valid(self, form):
        """
        Submit the form and log the user activity.
        """
        initial_field_dict = {field: form.initial[field] for field in form.initial.keys()}
        cleaned_data_field_dict = {field: form.cleaned_data[field] for field in form.cleaned_data.keys()}
        changed_fields_dict = DictDiffer(initial_field_dict, cleaned_data_field_dict).changed()
        if changed_fields_dict:
            verb_string = 'Changed values of Service : %s from initial values ' % (self.object.name) + ', '.join(
                ['%s: %s' % (k, initial_field_dict[k]) \
                 for k in changed_fields_dict]) + \
                          ' to ' + \
                          ', '.join(['%s: %s' % (k, cleaned_data_field_dict[k]) for k in changed_fields_dict])
            if len(verb_string) >= 255:
                verb_string = verb_string[:250] + '...'
            self.object = form.save()
        return HttpResponseRedirect(ServiceUpdate.success_url)


class ServiceDelete(PermissionsRequiredMixin, DeleteView):
    """
    Class Based View to Delete the Service.
    """
    model = Service
    template_name = 'service/service_delete.html'
    success_url = reverse_lazy('services_list')
    required_permissions = ('service.delete_service',)

    def delete(self, request, *args, **kwargs):
        """
        Overriding the delete method to log the user activity.
        """
        try:
            UserAction.objects.create(user_id=self.request.user.id, module='Service',
                         action='A service is deleted - {}'.format(self.get_object().alias) )
        except:
            pass
        return super(ServiceDelete, self).delete(request, *args, **kwargs)


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


class ServiceParametersListingTable(PermissionsRequiredMixin, BaseDatatableView):
    """
    Class based View to render ServiceParameters Data table.
    """
    model = ServiceParameters
    required_permissions = ('service.view_serviceparameters',)
    columns = ['parameter_description', 'protocol__name', 'normal_check_interval', 'retry_check_interval',
               'max_check_attempts']
    order_columns = ['parameter_description', 'protocol__name', 'normal_check_interval', 'retry_check_interval',
                     'max_check_attempts']

    def filter_queryset(self, qs):
        """
        The filtering of the queryset with respect to the search keyword entered.

        :param qs:
        :return qs:
        """
        sSearch = self.request.GET.get('sSearch', None)
        if sSearch:
            query = []
            exec_query = "qs = %s.objects.filter(" % (self.model.__name__)
            for column in self.columns:
                query.append("Q(%s__icontains=" % column + "\"" + sSearch + "\"" + ")")

            exec_query += " | ".join(query)
            exec_query += ").values(*" + str(self.columns + ['id']) + ")"
            exec exec_query

        return qs

    def get_initial_queryset(self):
        """
        Preparing  Initial Queryset for the for rendering the data table.

        """
        if not self.model:
            raise NotImplementedError("Need to provide a model or implement get_initial_queryset!")
        return ServiceParameters.objects.values(*self.columns + ['id'])

    def prepare_results(self, qs):
        """
        Preparing the final result after fetching from the data base to render on the data table.

        :param qs:
        :return qs

        """
        if qs:
            qs = [{key: val if val else "" for key, val in dct.items()} for dct in qs]
        for dct in qs:
            dct.update(actions='<a href="/service_parameter/edit/{0}"><i class="fa fa-pencil text-dark"></i></a>\
                <a href="/service_parameter/delete/{0}"><i class="fa fa-trash-o text-danger"></i></a>'.format(
                dct.pop('id')))
        return qs

    def get_context_data(self, *args, **kwargs):
        """
        The main function call to fetch, search, ordering , prepare and display the data on the data table.
        """
        request = self.request
        self.initialize(*args, **kwargs)

        qs = self.get_initial_queryset()

        # number of records before filtering
        total_records = qs.count()

        qs = self.filter_queryset(qs)

        # number of records after filtering
        total_display_records = qs.count()

        qs = self.ordering(qs)
        qs = self.paging(qs)
        #if the qs is empty then JSON is unable to serialize the empty ValuesQuerySet.Therefore changing its type to list.
        if not qs and isinstance(qs, ValuesQuerySet):
            qs = list(qs)

        # prepare output data
        aaData = self.prepare_results(qs)
        ret = {'sEcho': int(request.REQUEST.get('sEcho', 0)),
               'iTotalRecords': total_records,
               'iTotalDisplayRecords': total_display_records,
               'aaData': aaData
        }
        return ret


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

    def form_valid(self, form):
        """
        Submit the form and log the user activity.

        """
        self.object = form.save()
        return HttpResponseRedirect(ServiceParametersCreate.success_url)


class ServiceParametersUpdate(PermissionsRequiredMixin, UpdateView):
    """
    Class Based View to Update the Service Parameters.
    """
    template_name = 'service_parameter/service_parameter_update.html'
    model = ServiceParameters
    form_class = ServiceParametersForm
    success_url = reverse_lazy('services_parameter_list')
    required_permissions = ('service.change_serviceparameters',)

    def form_valid(self, form):
        """
        Submit the form and log the user activity.
        """
        initial_field_dict = {field: form.initial[field] for field in form.initial.keys()}

        cleaned_data_field_dict = {field: form.cleaned_data[field] for field in form.cleaned_data.keys()}

        changed_fields_dict = DictDiffer(initial_field_dict, cleaned_data_field_dict).changed()
        if changed_fields_dict:
            verb_string = 'Changed values of Service Paramters: %s from initial values ' % (
                self.object.parameter_description) \
                          + ', '.join(['%s: %s' % (k, initial_field_dict[k]) for k in changed_fields_dict]) \
                          + ' to ' \
                          + ', '.join(['%s: %s' % (k, cleaned_data_field_dict[k]) for k in changed_fields_dict])
            self.object = form.save()
        return HttpResponseRedirect(ServiceParametersUpdate.success_url)


class ServiceParametersDelete(PermissionsRequiredMixin, DeleteView):
    """
    Class Based View to Delete the ServiceParameters.
    """
    model = ServiceParameters
    template_name = 'service_parameter/service_parameter_delete.html'
    success_url = reverse_lazy('services_parameter_list')
    required_permissions = ('service.delete_serviceparameters',)

    def delete(self, request, *args, **kwargs):
        """
        Log the user activity before deleting the Service Parameters.
        """
        try:
            UserAction.objects.create(user_id=self.request.user.id, module='Service Parameters',
                         action='A service parameters is deleted - {}'.format(self.get_object().parameter_description) )
        except:
            pass
        return super(ServiceParametersDelete, self).delete(request, *args, **kwargs)


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


class ServiceDataSourceListingTable(PermissionsRequiredMixin, BaseDatatableView):
    model = ServiceDataSource
    required_permissions = ('service.view_servicedatasource',)
    columns = ['name', 'alias', 'warning', 'critical']
    order_columns = ['name', 'alias', 'warning', 'critical']

    def filter_queryset(self, qs):
        """
        The filtering of the queryset with respect to the search keyword entered.

        :param qs:
        :return qs:
        """
        sSearch = self.request.GET.get('sSearch', None)
        if sSearch:
            query = []
            exec_query = "qs = %s.objects.filter(" % (self.model.__name__)
            for column in self.columns:
                query.append("Q(%s__icontains=" % column + "\"" + sSearch + "\"" + ")")

            exec_query += " | ".join(query)
            exec_query += ").values(*" + str(self.columns + ['id']) + ")"
            exec exec_query

        return qs

    def get_initial_queryset(self):
        """
        Preparing  Initial Queryset for the for rendering the data table.
        """
        if not self.model:
            raise NotImplementedError("Need to provide a model or implement get_initial_queryset!")
        return ServiceDataSource.objects.values(*self.columns + ['id'])

    def prepare_results(self, qs):
        """
        Preparing the final result after fetching from the data base to render on the data table.

        :param qs:
        :return qs

        """
        if qs:
            qs = [{key: val if val else "" for key, val in dct.items()} for dct in qs]
        for dct in qs:
            dct.update(actions='<a href="/service_data_source/edit/{0}"><i class="fa fa-pencil text-dark"></i></a>\
                <a href="/service_data_source/delete/{0}"><i class="fa fa-trash-o text-danger"></i></a>'.format(
                dct.pop('id')))
        return qs

    def get_context_data(self, *args, **kwargs):
        """
        The main function call to fetch, search, ordering , prepare and display the data on the data table.
        """
        request = self.request
        self.initialize(*args, **kwargs)

        qs = self.get_initial_queryset()

        # number of records before filtering
        total_records = qs.count()

        qs = self.filter_queryset(qs)

        # number of records after filtering
        total_display_records = qs.count()

        qs = self.ordering(qs)
        qs = self.paging(qs)
        #if the qs is empty then JSON is unable to serialize the empty ValuesQuerySet.Therefore changing its type to list.
        if not qs and isinstance(qs, ValuesQuerySet):
            qs = list(qs)

        # prepare output data
        aaData = self.prepare_results(qs)
        ret = {'sEcho': int(request.REQUEST.get('sEcho', 0)),
               'iTotalRecords': total_records,
               'iTotalDisplayRecords': total_display_records,
               'aaData': aaData
        }
        return ret


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

    def form_valid(self, form):
        """
        Submit the form and log the user activity.
        """
        self.object = form.save()
        return HttpResponseRedirect(ServiceDataSourceCreate.success_url)


class ServiceDataSourceUpdate(PermissionsRequiredMixin, UpdateView):
    """
    Class based View to update the Service Data Source.
    """
    template_name = 'service_data_source/service_data_source_update.html'
    model = ServiceDataSource
    form_class = ServiceDataSourceForm
    success_url = reverse_lazy('service_data_sources_list')
    required_permissions = ('service.change_servicedatasource',)

    def form_valid(self, form):
        """
        Submit the form and log the user activity.
        """
        initial_field_dict = {field: form.initial[field] for field in form.initial.keys()}
        cleaned_data_field_dict = {field: form.cleaned_data[field] for field in form.cleaned_data.keys()}
        changed_fields_dict = DictDiffer(initial_field_dict, cleaned_data_field_dict).changed()
        if changed_fields_dict:
            verb_string = 'Changed values of ServiceDataSource : %s from initial values ' % (
                self.object.name) + ', '.join(['%s: %s' % (k, initial_field_dict[k]) \
                                               for k in changed_fields_dict]) + \
                          ' to ' + \
                          ', '.join(['%s: %s' % (k, cleaned_data_field_dict[k]) for k in changed_fields_dict])
            self.object = form.save()
        return HttpResponseRedirect(ServiceDataSourceUpdate.success_url)


class ServiceDataSourceDelete(PermissionsRequiredMixin, DeleteView):
    """
    Class Based View to Delete the Service Data Source.
    """
    model = ServiceDataSource
    template_name = 'service_data_source/service_data_source_delete.html'
    success_url = reverse_lazy('service_data_sources_list')
    required_permissions = ('service.delete_servicedatasource',)

    def delete(self, request, *args, **kwargs):
        """
        Overriding delete method to log the user activity.
        """
        try:
            UserAction.objects.create(user_id=self.request.user.id, module='Service Data Source',
                         action='A service sata source is deleted - {}'.format(self.get_object().alias) )
        except:
            pass
        return super(ServiceDataSourceDelete, self).delete(request, *args, **kwargs)


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


class ProtocolListingTable(PermissionsRequiredMixin, BaseDatatableView):
    """
    Class Based View to render the protocol Data table.
    """
    model = Protocol
    required_permissions = ('service.view_protocol',)
    columns = ['name', 'protocol_name', 'port', 'version', 'read_community', 'write_community', 'auth_password',
               'auth_protocol', 'security_name', 'security_level', 'private_phase', 'private_pass_phase']
    order_columns = ['name', 'protocol_name', 'port', 'version', 'read_community', 'write_community', 'auth_password',
                     'auth_protocol', 'security_name', 'security_level', 'private_phase', 'private_pass_phase']

    def filter_queryset(self, qs):
        """
        The filtering of the queryset with respect to the search keyword entered.

        :param qs:
        :return qs:

        """
        sSearch = self.request.GET.get('sSearch', None)
        if sSearch:
            query = []
            exec_query = "qs = %s.objects.filter(" % (self.model.__name__)
            for column in self.columns:
                query.append("Q(%s__icontains=" % column + "\"" + sSearch + "\"" + ")")

            exec_query += " | ".join(query)
            exec_query += ").values(*" + str(self.columns + ['id']) + ")"
            exec exec_query

        return qs

    def get_initial_queryset(self):
        """
        Preparing  Initial Queryset for the for rendering the data table.
        """
        if not self.model:
            raise NotImplementedError("Need to provide a model or implement get_initial_queryset!")
        return Protocol.objects.values(*self.columns + ['id'])

    def prepare_results(self, qs):
        """
        Preparing the final result after fetching from the data base to render on the data table.

        :param qs:
        :return qs
        """
        if qs:
            qs = [{key: val if val else "" for key, val in dct.items()} for dct in qs]
        for dct in qs:
            dct.update(actions='<a href="/protocol/edit/{0}"><i class="fa fa-pencil text-dark"></i></a>\
                <a href="/protocol/delete/{0}"><i class="fa fa-trash-o text-danger"></i></a>'.format(dct.pop('id')))
        return qs

    def get_context_data(self, *args, **kwargs):
        """
        The main function call to fetch, search, ordering , prepare and display the data on the data table.
        """
        request = self.request
        self.initialize(*args, **kwargs)

        qs = self.get_initial_queryset()

        # number of records before filtering
        total_records = qs.count()

        qs = self.filter_queryset(qs)

        # number of records after filtering
        total_display_records = qs.count()

        qs = self.ordering(qs)
        qs = self.paging(qs)
        #if the qs is empty then JSON is unable to serialize the empty ValuesQuerySet.Therefore changing its type to list.
        if not qs and isinstance(qs, ValuesQuerySet):
            qs = list(qs)

        # prepare output data
        aaData = self.prepare_results(qs)
        ret = {'sEcho': int(request.REQUEST.get('sEcho', 0)),
               'iTotalRecords': total_records,
               'iTotalDisplayRecords': total_display_records,
               'aaData': aaData
        }
        return ret


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


    def form_valid(self, form):
        """
        Submit the form and log the user activity.
        """
        self.object = form.save()
        return HttpResponseRedirect(ProtocolCreate.success_url)


class ProtocolUpdate(PermissionsRequiredMixin, UpdateView):
    """
    Class Based View to update the protocol.
    """
    template_name = 'protocol/protocol_update.html'
    model = Protocol
    form_class = ProtocolForm
    success_url = reverse_lazy('protocols_list')
    required_permissions = ('service.change_protocol',)

    def form_valid(self, form):
        """
        Submit the form and log the user activity.
        """
        initial_field_dict = {field: form.initial[field] for field in form.initial.keys()}
        cleaned_data_field_dict = {field: form.cleaned_data[field] for field in form.cleaned_data.keys()}
        changed_fields_dict = DictDiffer(initial_field_dict, cleaned_data_field_dict).changed()
        if changed_fields_dict:
            verb_string = 'Changed values of Protocol : %s from initial values ' % (self.object.name) + ', '.join(
                ['%s: %s' % (k, initial_field_dict[k]) \
                 for k in changed_fields_dict]) + \
                          ' to ' + \
                          ', '.join(['%s: %s' % (k, cleaned_data_field_dict[k]) for k in changed_fields_dict])
            self.object = form.save()
        return HttpResponseRedirect(ProtocolUpdate.success_url)

class ProtocolDelete(PermissionsRequiredMixin, DeleteView):
    """
    Class Based View to delete the protocol.
    """
    model = Protocol
    template_name = 'protocol/protocol_delete.html'
    success_url = reverse_lazy('protocols_list')
    required_permissions = ('service.delete_protocol',)

    def delete(self, request, *args, **kwargs):
        """
        Overriding the delete method to log the user activity.
        """
        try:
            protocol_obj = self.get_object()
            UserAction.objects.create(user_id=self.request.user.id, module='Protocol',
                         action='A protocol is deleted - {}(port - {}, version - {})'.format(protocol_obj.protocol_name,
                                                protocol_obj.port, protocol_obj.version) )
        except:
            pass
        return super(ProtocolDelete, self).delete( request, *args, **kwargs)


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

class DeviceServiceConfigurationListingTable(PermissionsRequiredMixin, BaseDatatableView):
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

    def filter_queryset(self, qs):
        """
        The filtering of the queryset with respect to the search keyword entered.

        :param qs:
        :return qs:

        """
        sSearch = self.request.GET.get('sSearch', None)
        if sSearch:
            query=[]
            exec_query = "qs = %s.objects.filter("%(self.model.__name__)
            for column in self.columns[:-2]:
                query.append("Q(%s__icontains="%column + "\"" +sSearch +"\"" +")")

            exec_query += " | ".join(query)
            exec_query += ").values(*"+str(self.columns+['id'])+")"
            exec exec_query

        return qs

    def get_initial_queryset(self):
        """
        Preparing  Initial Queryset for the for rendering the data table.
        """
        if not self.model:
            raise NotImplementedError("Need to provide a model or implement get_initial_queryset!")
        return DeviceServiceConfiguration.objects.values(*self.columns+['id'])

    def prepare_results(self, qs):
        """
        Preparing the final result after fetching from the data base to render on the data table.

        :param qs:
        :return qs
        """

        if qs:
            qs = [ { key: val if val else "" for key, val in dct.items() } for dct in qs ]
        for dct in qs:
            dct.update(actions='<a href="#" onclick="Dajaxice.device.edit_single_service_form(get_single_service_edit_form,\
                               {{\'dsc_id\': {0}}})"><i class="fa fa-pencil text-dark"></i></a>\
                                <a href="#" onclick="Dajaxice.device.delete_single_service_form(get_single_service_delete_form,\
                                {{\'dsc_id\': {0}}})"><i class="fa fa-trash-o text-danger"></i></a>'.format(dct.pop('id')),
                       added_on=dct['added_on'].strftime("%Y-%m-%d %H:%M:%S"),
                       modified_on=dct['modified_on'].strftime("%Y-%m-%d %H:%M:%S"))

        return qs

    def get_context_data(self, *args, **kwargs):
        """
        The main function call to fetch, search, ordering , prepare and display the data on the data table.
        """
        request = self.request
        self.initialize(*args, **kwargs)

        qs = self.get_initial_queryset()

        # number of records before filtering
        total_records = qs.count()

        qs = self.filter_queryset(qs)

        # number of records after filtering
        total_display_records = qs.count()

        qs = self.ordering(qs)
        qs = self.paging(qs)
        #if the qs is empty then JSON is unable to serialize the empty ValuesQuerySet.Therefore changing its type to list.
        if not qs and isinstance(qs, ValuesQuerySet):
            qs=list(qs)

        # prepare output data
        aaData = self.prepare_results(qs)
        ret = {'sEcho': int(request.REQUEST.get('sEcho', 0)),
               'iTotalRecords': total_records,
               'iTotalDisplayRecords': total_display_records,
               'aaData': aaData
               }
        return ret
