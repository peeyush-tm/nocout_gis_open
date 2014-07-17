import json
from actstream import action
from django.contrib.auth.decorators import permission_required
from django.db.models.query import ValuesQuerySet
from django.http import HttpResponseRedirect
from django.utils.decorators import method_decorator
from django.views.generic import ListView, DetailView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.core.urlresolvers import reverse_lazy
from django_datatables_view.base_datatable_view import BaseDatatableView
from models import Service, ServiceParameters, ServiceDataSource, Protocol, ServiceHistory
from .forms import ServiceForm, ServiceParametersForm, ServiceDataSourceForm, ProtocolForm
from nocout.utils.util import DictDiffer
from django.db.models import Q

# ########################################################
from django.conf import settings

if settings.DEBUG:
    import logging

    logger = logging.getLogger(__name__)
#########################################################


# **************************************** Service *********************************************
class ServiceList(ListView):
    model = Service
    template_name = 'service/services_list.html'

    def get_context_data(self, **kwargs):
        context = super(ServiceList, self).get_context_data(**kwargs)
        datatable_headers = [
            {'mData': 'name', 'sTitle': 'Name', 'sWidth': 'null', },
            {'mData': 'alias', 'sTitle': 'Alias', 'sWidth': 'null', 'sClass': 'hidden-xs'},
            {'mData': 'parameters__parameter_description', 'sTitle': 'Default Parameters', 'sWidth': 'null', },
            {'mData': 'service_data_sources__alias', 'sTitle': 'Data Sources', 'sWidth': 'null', },
            {'mData': 'description', 'sTitle': 'Description', 'sWidth': 'null', 'sClass': 'hidden-xs'},
            {'mData': 'actions', 'sTitle': 'Actions', 'sWidth': '5%', }]

        context['datatable_headers'] = json.dumps(datatable_headers)
        return context


class ServiceListingTable(BaseDatatableView):
    model = Service
    columns = ['name', 'alias', 'parameters__parameter_description', 'service_data_sources__alias', 'description']
    order_columns = ['name', 'alias', 'parameters__parameter_description', 'description']

    def filter_queryset(self, qs):
        sSearch = self.request.GET.get('sSearch', None)
        ##TODO:Need to optimise with the query making login.
        if sSearch:
            query = []
            exec_query = "qs = %s.objects.filter(" % (self.model.__name__)
            for column in self.columns[:-1]:
                query.append("Q(%s__contains=" % column + "\"" + sSearch + "\"" + ")")

            exec_query += " | ".join(query)
            exec_query += ").values(*" + str(self.columns + ['id']) + ")"
            exec exec_query

        return qs

    def get_initial_queryset(self):
        if not self.model:
            raise NotImplementedError("Need to provide a model or implement get_initial_queryset!")
        return Service.objects.values(*self.columns + ['id'])

    def prepare_results(self, qs):
        if qs:
            qs = [{key: val if val else "" for key, val in dct.items()} for dct in qs]

        ##joining the multiple data sources in one
        new_qs = []
        temp_dict = {}
        delete_list = []
        for ds in qs:
            if ds["id"] not in temp_dict:
                temp_dict[ds["id"]] = []
            temp_dict[ds["id"]].append(ds["service_data_sources__alias"])

        for q in qs:
            if q["id"] not in delete_list:
                delete_list.append(q["id"])
                for sid in temp_dict:
                    if sid == q["id"]:
                        q["service_data_sources__alias"] = ", ".join(temp_dict[sid])
                        new_qs.append(q)
        ##joining the multiple data sources in one.
        ## replacing old one
        qs = new_qs
        ## replacing old one

        for dct in qs:
            dct.update(actions='<a href="/service/edit/{0}"><i class="fa fa-pencil text-dark"></i></a>\
                <a href="/service/delete/{0}"><i class="fa fa-trash-o text-danger"></i></a>'.format(dct.pop('id')))
        return qs

    def get_context_data(self, *args, **kwargs):
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


class ServiceDetail(DetailView):
    model = Service
    template_name = 'service/service_detail.html'


class ServiceCreate(CreateView):
    template_name = 'service/service_new.html'
    model = Service
    form_class = ServiceForm
    success_url = reverse_lazy('services_list')

    @method_decorator(permission_required('service.add_service', raise_exception=True))
    def dispatch(self, *args, **kwargs):
        return super(ServiceCreate, self).dispatch(*args, **kwargs)


    def form_valid(self, form):
        self.object = form.save()
        action.send(self.request.user, verb='Created', action_object=self.object)
        return HttpResponseRedirect(ServiceCreate.success_url)


class ServiceUpdate(UpdateView):
    template_name = 'service/service_update.html'
    model = Service
    form_class = ServiceForm
    success_url = reverse_lazy('services_list')

    @method_decorator(permission_required('service.change_service', raise_exception=True))
    def dispatch(self, *args, **kwargs):
        return super(ServiceUpdate, self).dispatch(*args, **kwargs)


    def form_valid(self, form):
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
            action.send(self.request.user, verb=verb_string)
        return HttpResponseRedirect(ServiceUpdate.success_url)


class ServiceDelete(DeleteView):
    model = Service
    template_name = 'service/service_delete.html'
    success_url = reverse_lazy('services_list')

    @method_decorator(permission_required('service.delete_service', raise_exception=True))
    def dispatch(self, *args, **kwargs):
        return super(ServiceDelete, self).dispatch(*args, **kwargs)

    def delete(self, request, *args, **kwargs):
        action.send(request.user, verb='deleting services: %s' % (self.get_object().name))
        return super(ServiceDelete, self).delete(request, *args, **kwargs)


#************************************* Service Parameters *****************************************
class ServiceParametersList(ListView):
    model = ServiceParameters
    template_name = 'service_parameter/services_parameter_list.html'

    def get_context_data(self, **kwargs):
        context = super(ServiceParametersList, self).get_context_data(**kwargs)
        datatable_headers = [
            {'mData': 'parameter_description', 'sTitle': 'Parameter Description', 'sWidth': 'null', },
            {'mData': 'protocol__name', 'sTitle': 'Protocol', 'sWidth': 'null', },
            {'mData': 'normal_check_interval', 'sTitle': 'Normal Check Intervals', 'sWidth': 'null',
             'sClass': 'hidden-xs'},
            {'mData': 'retry_check_interval', 'sTitle': 'Retry Check Intervals', 'sWidth': 'null', },
            {'mData': 'max_check_attempts', 'sTitle': 'Max Check Attempts', 'sWidth': 'null', },
            {'mData': 'actions', 'sTitle': 'Actions', 'sWidth': '5%', }
        ]
        context['datatable_headers'] = json.dumps(datatable_headers)
        return context


class ServiceParametersListingTable(BaseDatatableView):
    model = ServiceParameters
    columns = ['parameter_description', 'protocol__name', 'normal_check_interval', 'retry_check_interval',
               'max_check_attempts']
    order_columns = ['parameter_description', 'protocol__name', 'normal_check_interval', 'retry_check_interval',
                     'max_check_attempts']

    def filter_queryset(self, qs):
        sSearch = self.request.GET.get('sSearch', None)
        ##TODO:Need to optimise with the query making login.
        if sSearch:
            query = []
            exec_query = "qs = %s.objects.filter(" % (self.model.__name__)
            for column in self.columns[:-1]:
                query.append("Q(%s__contains=" % column + "\"" + sSearch + "\"" + ")")

            exec_query += " | ".join(query)
            exec_query += ").values(*" + str(self.columns + ['id']) + ")"
            # qs=qs.filter( reduce( lambda q, column: q | Q(column__contains=sSearch), self.columns, Q() ))
            # qs = qs.filter(Q(username__contains=sSearch) | Q(first_name__contains=sSearch) | Q() )
            exec exec_query

        return qs

    def get_initial_queryset(self):
        if not self.model:
            raise NotImplementedError("Need to provide a model or implement get_initial_queryset!")
        return ServiceParameters.objects.values(*self.columns + ['id'])

    def prepare_results(self, qs):
        if qs:
            qs = [{key: val if val else "" for key, val in dct.items()} for dct in qs]
        for dct in qs:
            dct.update(actions='<a href="/service_parameter/edit/{0}"><i class="fa fa-pencil text-dark"></i></a>\
                <a href="/service_parameter/delete/{0}"><i class="fa fa-trash-o text-danger"></i></a>'.format(
                dct.pop('id')))
        return qs

    def get_context_data(self, *args, **kwargs):
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


class ServiceParametersDetail(DetailView):
    model = ServiceParameters
    template_name = 'service_parameter/service_parameter_detail.html'


class ServiceParametersCreate(CreateView):
    template_name = 'service_parameter/service_parameter_new.html'
    model = ServiceParameters
    form_class = ServiceParametersForm
    success_url = reverse_lazy('services_parameter_list')

    @method_decorator(permission_required('service.add_serviceparameters', raise_exception=True))
    def dispatch(self, *args, **kwargs):
        return super(ServiceParametersCreate, self).dispatch(*args, **kwargs)

    def form_valid(self, form):
        self.object = form.save()
        action.send(self.request.user, verb='Created', action_object=self.object)
        return HttpResponseRedirect(ServiceParametersCreate.success_url)


class ServiceParametersUpdate(UpdateView):
    template_name = 'service_parameter/service_parameter_update.html'
    model = ServiceParameters
    form_class = ServiceParametersForm
    success_url = reverse_lazy('services_parameter_list')

    @method_decorator(permission_required('service.change_serviceparameters', raise_exception=True))
    def dispatch(self, *args, **kwargs):
        return super(ServiceParametersUpdate, self).dispatch(*args, **kwargs)


    def form_valid(self, form):
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
            action.send(self.request.user, verb=verb_string)
        return HttpResponseRedirect(ServiceParametersUpdate.success_url)


class ServiceParametersDelete(DeleteView):
    model = ServiceParameters
    template_name = 'service_parameter/service_parameter_delete.html'
    success_url = reverse_lazy('services_parameter_list')

    @method_decorator(permission_required('service.delete_serviceparameters', raise_exception=True))
    def dispatch(self, *args, **kwargs):
        return super(ServiceParametersDelete, self).dispatch(*args, **kwargs)

    def delete(self, request, *args, **kwargs):
        action.send(request.user, verb='deleting services parameters: %s' % (self.get_object().parameter_description))
        return super(ServiceParametersDelete, self).delete(request, *args, **kwargs)


#********************************** Service Data Source ***************************************
class ServiceDataSourceList(ListView):
    model = ServiceDataSource
    template_name = 'service_data_source/service_data_sources_list.html'

    def get_context_data(self, **kwargs):
        context = super(ServiceDataSourceList, self).get_context_data(**kwargs)
        datatable_headers = [
            {'mData': 'name', 'sTitle': 'Name', 'sWidth': 'null', },
            {'mData': 'alias', 'sTitle': 'Alias', 'sWidth': 'null', 'sClass': 'hidden-xs'},
            {'mData': 'warning', 'sTitle': 'Warning', 'sWidth': 'null', },
            {'mData': 'critical', 'sTitle': 'Critical', 'sWidth': 'null', 'sClass': 'hidden-xs'},
            {'mData': 'actions', 'sTitle': 'Actions', 'sWidth': '10%', }
        ]
        context['datatable_headers'] = json.dumps(datatable_headers)
        return context


class ServiceDataSourceListingTable(BaseDatatableView):
    model = ServiceDataSourceList
    columns = ['name', 'alias', 'warning', 'critical']
    order_columns = ['name', 'alias', 'warning', 'critical']

    def filter_queryset(self, qs):
        sSearch = self.request.GET.get('sSearch', None)
        ##TODO:Need to optimise with the query making login.
        if sSearch:
            query = []
            exec_query = "qs = %s.objects.filter(" % (self.model.__name__)
            for column in self.columns[:-1]:
                query.append("Q(%s__contains=" % column + "\"" + sSearch + "\"" + ")")

            exec_query += " | ".join(query)
            exec_query += ").values(*" + str(self.columns + ['id']) + ")"
            # qs=qs.filter( reduce( lambda q, column: q | Q(column__contains=sSearch), self.columns, Q() ))
            # qs = qs.filter(Q(username__contains=sSearch) | Q(first_name__contains=sSearch) | Q() )
            exec exec_query

        return qs

    def get_initial_queryset(self):
        if not self.model:
            raise NotImplementedError("Need to provide a model or implement get_initial_queryset!")
        return ServiceDataSource.objects.values(*self.columns + ['id'])

    def prepare_results(self, qs):
        if qs:
            qs = [{key: val if val else "" for key, val in dct.items()} for dct in qs]
        for dct in qs:
            dct.update(actions='<a href="/service_data_source/edit/{0}"><i class="fa fa-pencil text-dark"></i></a>\
                <a href="/service_data_source/delete/{0}"><i class="fa fa-trash-o text-danger"></i></a>'.format(
                dct.pop('id')))
        return qs

    def get_context_data(self, *args, **kwargs):
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


class ServiceDataSourceDetail(DetailView):
    model = ServiceDataSource
    template_name = 'service_data_source/service_data_source_detail.html'


class ServiceDataSourceCreate(CreateView):
    template_name = 'service_data_source/service_data_source_new.html'
    model = ServiceDataSource
    form_class = ServiceDataSourceForm
    success_url = reverse_lazy('service_data_sources_list')

    @method_decorator(permission_required('service.add_servicedatasource', raise_exception=True))
    def dispatch(self, *args, **kwargs):
        return super(ServiceDataSourceCreate, self).dispatch(*args, **kwargs)


    def form_valid(self, form):
        self.object = form.save()
        action.send(self.request.user, verb='Created', action_object=self.object)
        return HttpResponseRedirect(ServiceDataSourceCreate.success_url)


class ServiceDataSourceUpdate(UpdateView):
    template_name = 'service_data_source/service_data_source_update.html'
    model = ServiceDataSource
    form_class = ServiceDataSourceForm
    success_url = reverse_lazy('service_data_sources_list')

    @method_decorator(permission_required('service.change_servicedatasource', raise_exception=True))
    def dispatch(self, *args, **kwargs):
        return super(ServiceDataSourceUpdate, self).dispatch(*args, **kwargs)

    def form_valid(self, form):
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
            action.send(self.request.user, verb=verb_string)
        return HttpResponseRedirect(ServiceDataSourceUpdate.success_url)


class ServiceDataSourceDelete(DeleteView):
    model = ServiceDataSource
    template_name = 'service_data_source/service_data_source_delete.html'
    success_url = reverse_lazy('service_data_sources_list')

    @method_decorator(permission_required('service.delete_servicedatasource', raise_exception=True))
    def dispatch(self, *args, **kwargs):
        return super(ServiceDataSourceDelete, self).dispatch(*args, **kwargs)

    def delete(self, request, *args, **kwargs):
        action.send(request.user, verb='deleting services data source: %s' % (self.get_object().name))
        return super(ServiceDataSourceDelete, self).delete(request, *args, **kwargs)


#********************************** Protocol ***************************************
class ProtocolList(ListView):
    model = Protocol
    template_name = 'protocol/protocols_list.html'

    def get_context_data(self, **kwargs):
        context = super(ProtocolList, self).get_context_data(**kwargs)
        datatable_headers = [
            {'mData': 'name', 'sTitle': 'Name', 'sWidth': 'null', },
            {'mData': 'protocol_name', 'sTitle': 'Protocol Name', 'sWidth': 'null', 'sClass': 'hidden-xs'},
            {'mData': 'port', 'sTitle': 'Port', 'sWidth': 'null', },
            {'mData': 'version', 'sTitle': 'Version', 'sWidth': 'null', 'sClass': 'hidden-xs'},
            {'mData': 'read_community', 'sTitle': 'Read Community', 'sWidth': 'null', },
            {'mData': 'write_community', 'sTitle': 'Write Community', 'sWidth': 'null', 'sClass': 'hidden-xs'},
            {'mData': 'auth_password', 'sTitle': 'Auth Password', 'sWidth': 'null', },
            {'mData': 'auth_protocol', 'sTitle': 'Auth Protocol', 'sWidth': 'null', 'sClass': 'hidden-xs'},
            {'mData': 'security_name', 'sTitle': 'Security Name', 'sWidth': 'null', },
            {'mData': 'security_level', 'sTitle': 'Security Level', 'sWidth': 'null', 'sClass': 'hidden-xs'},
            {'mData': 'private_phase', 'sTitle': 'Private Phase', 'sWidth': 'null', },
            {'mData': 'private_pass_phase', 'sTitle': 'Private Pass Phase', 'sWidth': 'null', 'sClass': 'hidden-xs'},
            {'mData': 'actions', 'sTitle': 'Actions', 'sWidth': '10%', }
        ]
        context['datatable_headers'] = json.dumps(datatable_headers)
        return context


class ProtocolListingTable(BaseDatatableView):
    model = ProtocolList
    columns = ['name', 'protocol_name', 'port', 'version', 'read_community', 'write_community', 'auth_password',
               'auth_protocol', 'security_name', 'security_level', 'private_phase', 'private_pass_phase']
    order_columns = ['name', 'protocol_name', 'port', 'version', 'read_community', 'write_community', 'auth_password',
                     'auth_protocol', 'security_name', 'security_level', 'private_phase', 'private_pass_phase']

    def filter_queryset(self, qs):
        sSearch = self.request.GET.get('sSearch', None)
        ##TODO:Need to optimise with the query making login.
        if sSearch:
            query = []
            exec_query = "qs = %s.objects.filter(" % (self.model.__name__)
            for column in self.columns[:-1]:
                query.append("Q(%s__contains=" % column + "\"" + sSearch + "\"" + ")")

            exec_query += " | ".join(query)
            exec_query += ").values(*" + str(self.columns + ['id']) + ")"
            # qs=qs.filter( reduce( lambda q, column: q | Q(column__contains=sSearch), self.columns, Q() ))
            # qs = qs.filter(Q(username__contains=sSearch) | Q(first_name__contains=sSearch) | Q() )
            exec exec_query

        return qs

    def get_initial_queryset(self):
        if not self.model:
            raise NotImplementedError("Need to provide a model or implement get_initial_queryset!")
        return Protocol.objects.values(*self.columns + ['id'])

    def prepare_results(self, qs):
        if qs:
            qs = [{key: val if val else "" for key, val in dct.items()} for dct in qs]
        for dct in qs:
            dct.update(actions='<a href="/protocol/edit/{0}"><i class="fa fa-pencil text-dark"></i></a>\
                <a href="/protocol/delete/{0}"><i class="fa fa-trash-o text-danger"></i></a>'.format(dct.pop('id')))
        return qs

    def get_context_data(self, *args, **kwargs):
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


class ProtocolDetail(DetailView):
    model = Protocol
    template_name = 'protocol/protocol_detail.html'


class ProtocolCreate(CreateView):
    template_name = 'protocol/protocol_new.html'
    model = Protocol
    form_class = ProtocolForm
    success_url = reverse_lazy('protocols_list')

    @method_decorator(permission_required('service.add_protocol', raise_exception=True))
    def dispatch(self, *args, **kwargs):
        return super(ProtocolCreate, self).dispatch(*args, **kwargs)


    def form_valid(self, form):
        self.object = form.save()
        action.send(self.request.user, verb='Created', action_object=self.object)
        return HttpResponseRedirect(ProtocolCreate.success_url)


class ProtocolUpdate(UpdateView):
    template_name = 'protocol/protocol_update.html'
    model = Protocol
    form_class = ProtocolForm
    success_url = reverse_lazy('protocols_list')

    @method_decorator(permission_required('service.change_protocol', raise_exception=True))
    def dispatch(self, *args, **kwargs):
        return super(ProtocolUpdate, self).dispatch(*args, **kwargs)

    def form_valid(self, form):
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
            action.send(self.request.user, verb=verb_string)
        return HttpResponseRedirect(ProtocolUpdate.success_url)

class ProtocolDelete(DeleteView):
    model = Protocol
    template_name = 'protocol/protocol_delete.html'
    success_url = reverse_lazy('protocols_list')

    @method_decorator(permission_required('service.delete_protocol', raise_exception=True))
    def dispatch(self, *args, **kwargs):
        return super(ProtocolDelete, self).dispatch(*args, **kwargs)

    def delete(self, request, *args, **kwargs):
        action.send(request.user, verb='deleting services data source: %s'%(self.get_object().name))
        return super(ProtocolDelete, self).delete( request, *args, **kwargs)

    
#**************************************** ServiceHistory *********************************************
class ServiceHistoryList(ListView):
    model = ServiceHistory
    template_name = 'service_history/services_list.html'

    def get_context_data(self, **kwargs):
        context=super(ServiceHistoryList, self).get_context_data(**kwargs)
        datatable_headers = [
            {'mData':'device_name',             'sTitle' : 'Device',                'sWidth':'null',},
            {'mData':'service_name',            'sTitle' : 'Service',                 'sWidth':'null',},
            {'mData':'agent_tag',               'sTitle' : 'Agent Tag',             'sWidth':'null',},
            {'mData':'port',                    'sTitle' : 'Port',                  'sWidth':'null',},
            {'mData':'version',                 'sTitle' : 'Version',               'sWidth':'null',},
            {'mData':'data_source',             'sTitle' : 'DS',                    'sWidth':'null' ,},
            {'mData':'read_community',          'sTitle' : 'Read Community',        'sWidth':'null',},
            {'mData':'normal_check_interval',   'sTitle' : 'Normal CI',             'sWidth':'null',},
            {'mData':'retry_check_interval',    'sTitle' : 'Retry CI',              'sWidth':'null',},
            {'mData':'max_check_attempts',      'sTitle' : 'Max Attempts',          'sWidth':'null',},
            {'mData':'warning',                 'sTitle' : 'Warning',               'sWidth':'null',},
            {'mData':'critical',                'sTitle' : 'Critical',              'sWidth':'null',}]

        context['datatable_headers'] = json.dumps(datatable_headers)
        return context

class ServiceHistoryListingTable(BaseDatatableView):
    model = ServiceHistory
    columns = ['device_name', 'service_name', 'agent_tag', 'port', 'version', 'data_source', 'read_community', 'normal_check_interval', 'retry_check_interval', 'max_check_attempts', 'warning', 'critical']
    order_columns = ['device_name', 'service_name', 'agent_tag', 'port', 'version', 'data_source', 'read_community', 'normal_check_interval', 'retry_check_interval', 'max_check_attempts', 'warning', 'critical']

    def filter_queryset(self, qs):
        sSearch = self.request.GET.get('sSearch', None)
        if sSearch:
            query=[]
            exec_query = "qs = %s.objects.filter("%(self.model.__name__)
            for column in self.columns[:-1]:
                query.append("Q(%s__contains="%column + "\"" +sSearch +"\"" +")")

            exec_query += " | ".join(query)
            exec_query += ").values(*"+str(self.columns+['id'])+")"
            exec exec_query

        return qs

    def get_initial_queryset(self):
        if not self.model:
            raise NotImplementedError("Need to provide a model or implement get_initial_queryset!")
        return ServiceHistory.objects.values(*self.columns+['id'])

    def prepare_results(self, qs):
        if qs:
            qs = [ { key: val if val else "" for key, val in dct.items() } for dct in qs ]
        for dct in qs:
            dct.update(actions='<a href="/service/edit/{0}"><i class="fa fa-pencil text-dark"></i></a>\
                <a href="/service/delete/{0}"><i class="fa fa-trash-o text-danger"></i></a>'.format(dct.pop('id')))
        return qs

    def get_context_data(self, *args, **kwargs):
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
