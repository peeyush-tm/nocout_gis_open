import json

from django.core.urlresolvers import reverse_lazy
from django.db.models import Q
from django.db.models.query import ValuesQuerySet
from django.shortcuts import render, render_to_response
from django.http import HttpResponse
from django.views.generic import ListView, DetailView
from django.views.generic.base import View
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import user_passes_test
from django_datatables_view.base_datatable_view import BaseDatatableView

from nocout.utils import logged_in_user_organizations
from device.models import DeviceTechnology
from performance.models import ServiceStatus, NetworkAvailabilityDaily
from performance.views import organization_customer_devices, organization_network_devices
from dashboard.models import DashboardSetting
from dashboard.forms import DashboardSettingForm
from dashboard.utils import get_service_status_results, get_dashboard_status_range_counter, get_pie_chart_json_response_dict
from dashboard.config import dashboards
from activity_stream.models import UserAction


class DashbaordSettingsListView(ListView):
    """
    Class Based Dashboard-Settings View to render list page.
    """
    model = DashboardSetting
    template_name = 'dashboard/dashboard_settings_list.html'

    def get_queryset(self):
        """
        In this view no data is passed to datatable while rendering template.
        Another ajax call is made to fill in datatable.
        """
        queryset = super(DashbaordSettingsListView, self).get_queryset()
        queryset = queryset.none()
        return queryset

    def get_context_data(self, **kwargs):
        """
        Preparing the Context Variable required in the template rendering.
        """
        context = super(DashbaordSettingsListView, self).get_context_data(**kwargs)
        datatable_headers = [
            {'mData': 'page_name', 'sTitle': 'Page Name', 'sWidth': 'auto', },
            {'mData': 'technology__name', 'sTitle': 'Technology Name', 'sWidth': 'auto', },
            {'mData': 'name', 'sTitle': 'Dashboard Name', 'sWidth': 'auto', },
            {'mData': 'range1', 'sTitle': 'Range 1', 'sWidth': 'auto', 'bSortable': False },
            {'mData': 'range2', 'sTitle': 'Range 2', 'sWidth': 'auto', 'bSortable': False },
            {'mData': 'range3', 'sTitle': 'Range 3', 'sWidth': 'auto', 'bSortable': False },
            {'mData': 'range4', 'sTitle': 'Range 4', 'sWidth': 'auto', 'bSortable': False },
            {'mData': 'range5', 'sTitle': 'Range 5', 'sWidth': 'auto', 'bSortable': False },
            {'mData': 'range6', 'sTitle': 'Range 6', 'sWidth': 'auto', 'bSortable': False },
            {'mData': 'range7', 'sTitle': 'Range 7', 'sWidth': 'auto', 'bSortable': False },
            {'mData': 'range8', 'sTitle': 'Range 8', 'sWidth': 'auto', 'bSortable': False },
            {'mData': 'range9', 'sTitle': 'Range 9', 'sWidth': 'auto', 'bSortable': False },
            {'mData': 'range10', 'sTitle': 'Range 10', 'sWidth': 'auto', 'bSortable': False },
        ]

        #if the user is superuser then the action column will appear on the datatable
        if self.request.user.is_superuser:
            datatable_headers.append({'mData': 'actions', 'sTitle': 'Actions', 'sWidth': '5%', 'bSortable': False })

        context['datatable_headers'] = json.dumps(datatable_headers)
        return context


class DashbaordSettingsListingTable(BaseDatatableView):
    """
    Class based View to render Dashboard Settings Data table.
    """
    model = DashboardSetting
    columns = ['page_name', 'name', 'technology__name', 'range1', 'range2', 'range3', 'range4', 'range5', 'range6', 'range7', 'range8', 'range9', 'range10']
    keys = ['page_name', 'technology__name', 'name', 'range1_start', 'range2_start', 'range3_start', 'range4_start', 'range5_start', 'range6_start', 'range7_start', 'range8_start', 'range9_start', 'range10_start', 'range1_end', 'range2_end', 'range3_end', 'range4_end', 'range5_end', 'range6_end', 'range7_end', 'range8_end', 'range9_end', 'range10_end', 'range1_color_hex_value', 'range2_color_hex_value', 'range3_color_hex_value', 'range4_color_hex_value', 'range5_color_hex_value', 'range6_color_hex_value', 'range7_color_hex_value', 'range8_color_hex_value', 'range9_color_hex_value', 'range10_color_hex_value']
    order_columns = ['page_name', 'name', 'technology__name']

    def filter_queryset(self, qs):
        """
        The filtering of the queryset with respect to the search keyword entered.

        :param qs:
        :return qs:
        """
        sSearch = self.request.GET.get('sSearch', None)
        if sSearch:
            sSearch = sSearch.replace("\\", "")
            query = []
            exec_query = "qs = %s.objects.filter(" % (self.model.__name__)
            for column in self.keys[:-1]:
                query.append("Q(%s__icontains=" % column + "\"" + sSearch + "\"" + ")")

            exec_query += " | ".join(query)
            exec_query += ").values(*" + str(self.keys + ['id']) + ")"
            exec exec_query

        return qs

    def get_initial_queryset(self):
        """
        Preparing  Initial Queryset for the for rendering the data table.
        """
        if not self.model:
            raise NotImplementedError("Need to provide a model or implement get_initial_queryset!")
        return DashboardSetting.objects.values(*self.keys + ['id'])

    def prepare_results(self, qs):
        """
        Preparing the final result after fetching from the data base to render on the data table.

        :param qs:
        :return qs

        """
        if qs:
            qs_dict_list = [{key: val if val else "" for key, val in dct.items()} for dct in qs]
            for obj in qs_dict_list:
                for i in range(1, 11):
                    range_start = obj.pop('range%d_start' %i)
                    range_end = obj.pop('range%d_end' %i)
                    color_hex_value = obj.pop('range%d_color_hex_value' %i)
                    range_color = "<div style='display:block; height:20px; width:20px;\
                            background:{0}'></div>".format(color_hex_value)
                    if range_start:
                        obj.update({'range%d' %i : "(%s -<br>%s)<br>%s" % (range_start, range_end, range_color)})
                    else:
                        obj.update({'range%d' %i : ""})

                # Add actions to obj.
                obj_id = obj.pop('id')
                edit_url = reverse_lazy('dashboard-settings-update', kwargs={'pk': obj_id})
                delete_url = reverse_lazy('dashboard-settings-delete', kwargs={'pk': obj_id})
                edit_action = '<a href="%s"><i class="fa fa-pencil text-dark"></i></a>' % edit_url
                delete_action = '<a href="%s"><i class="fa fa-trash-o text-danger"></i></a>' % delete_url
                obj.update({'actions': edit_action + ' ' + delete_action})
            return qs_dict_list
        return qs

    def get_context_data(self, *args, **kwargs):
        """
        The main method call to fetch, search, ordering , prepare and display the data on the data table.
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


class DashbaordSettingsCreateView(CreateView):
    """
    Class based view to create new Dashboard Setting.
    """
    model = DashboardSetting
    form_class = DashboardSettingForm
    template_name = "dashboard/dashboard_settings_new.html"
    success_url = reverse_lazy('dashboard-settings')

    @method_decorator(user_passes_test(lambda u: u.is_superuser))
    def dispatch(self, *args, **kwargs):
        """
        The request dispatch method restricted with the permissions.
        """
        return super(DashbaordSettingsCreateView, self).dispatch(*args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(DashbaordSettingsCreateView, self).get_context_data(**kwargs)
        context['dashboards'] = json.dumps(dashboards)
        technology_options = dict(DeviceTechnology.objects.values_list('name', 'id'))
        context['technology_options'] = json.dumps(technology_options)
        return context


class DashbaordSettingsDetailView(DetailView):
    """
    Class based view to render the Dashboard Setting detail.
    """
    model = DashboardSetting
    template_name = 'dashboard/dashboard_detail.html'


class DashbaordSettingsUpdateView(UpdateView):
    """
    Class based view to update Dashboard Setting.
    """
    model = DashboardSetting
    form_class = DashboardSettingForm
    template_name = "dashboard/dashboard_settings_update.html"
    success_url = reverse_lazy('dashboard-settings')

    @method_decorator(user_passes_test(lambda u: u.is_superuser))
    def dispatch(self, *args, **kwargs):
        """
        The request dispatch method restricted with the permissions.
        """
        return super(DashbaordSettingsUpdateView, self).dispatch(*args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(DashbaordSettingsUpdateView, self).get_context_data(**kwargs)
        context['dashboards'] = json.dumps(dashboards)
        technology_options = dict(DeviceTechnology.objects.values_list('name', 'id'))
        context['technology_options'] = json.dumps(technology_options)
        return context


class DashbaordSettingsDeleteView(DeleteView):
    """
    Class based View to delete the Dashboard Setting.

    """
    model = DashboardSetting
    template_name = 'dashboard/dashboard_settings_delete.html'
    success_url = reverse_lazy('dashboard-settings')

    @method_decorator(user_passes_test(lambda u: u.is_superuser))
    def dispatch(self, *args, **kwargs):
        """
        The request dispatch method restricted with the permissions.
        """
        return super(DashbaordSettingsDeleteView, self).dispatch(*args, **kwargs)

    @method_decorator(user_passes_test(lambda u: u.is_superuser))
    def delete(self, request, *args, **kwargs):
        """
        Overriding the delete method to log the user activity.
        """
        try:
            obj = self.get_object()
            technology = DeviceTechnology.objects.get(id=obj.technology.id).alias
            action='A dashboard settings is deleted - {}(Technology- {})'.format(obj.name, technology)
            UserAction.objects.create(user_id=self.request.user.id, module='Dashboard Setting', action=action)
        except:
            pass
        return super(DashbaordSettingsDeleteView, self).delete(request, *args, **kwargs)



#****************************************** RF PERFORMANCE DASHBOARD ********************************************


class PerformanceDashboardMixin(object):
    """
    Provide common method get for Performance Dashboard.

    To use this Mixin set `template_name` and implement method get_init_data to provide following attributes:

        - data_source_config
        - technology
        - devices_method_to_call
        - devices_method_kwargs
    """

    def get(self, request):
        """
        Handles the get request

        :param request:
        :return Http response object:
        """
        data_source_config, technology, devices_method_to_call, devices_method_kwargs, is_bh = self.get_init_data()
        template_dict = {'data_sources': json.dumps(data_source_config.keys())}

        data_source = request.GET.get('data_source')
        if not data_source:
            return render(self.request, self.template_name, dictionary=template_dict)

        # Get Service Name from queried data_source
        try:
            service_name = data_source_config[data_source]['service_name']
            model = data_source_config[data_source]['model']
        except KeyError as e:
            return render(self.request, self.template_name, dictionary=template_dict)

        try:
            dashboard_setting = DashboardSetting.objects.get(technology=technology, page_name='rf_dashboard', name=data_source, is_bh=is_bh)
        except DashboardSetting.DoesNotExist as e:
            return HttpResponse(json.dumps({
                "message": "Corresponding dashboard seting is not available.",
                "success": 0
            }))

        # Get User's organizations
        # (admin : organization + sub organization)
        # (operator + viewer : same organization)
        user_organizations = logged_in_user_organizations(self)

        # Get Devices of User's Organizations. [and are Sub Station]
        user_devices = devices_method_to_call(user_organizations, technology, **devices_method_kwargs)

        service_status_results = get_service_status_results(
            user_devices, model=model, service_name=service_name, data_source=data_source
        )

        range_counter = get_dashboard_status_range_counter(dashboard_setting, service_status_results)

        response_dict = get_pie_chart_json_response_dict(dashboard_setting, data_source, range_counter)

        return HttpResponse(json.dumps(response_dict))


class WiMAX_Performance_Dashboard(View):
    """
    The Class based View to get performance dashboard page requested.

    """

    def get(self, request):
        """
        Handles the get request

        :param request:
        :return Http response object:
        """
        return render(self.request, 'home/home.html')


class PMP_Performance_Dashboard(PerformanceDashboardMixin, View):
    """
    The Class based View to get performance dashboard page requested.

    """
    template_name = 'rf_performance/pmp.html'

    def get_init_data(self):
        """
        Provide data for mixin's get method.
        """

        data_source_config = {
            'ul_jitter': {'service_name': 'cambium_ul_jitter', 'model': ServiceStatus},
            'dl_jitter': {'service_name': 'cambium_dl_jitter', 'model': ServiceStatus},
            'rereg_count': {'service_name': 'cambium_rereg_count', 'model': ServiceStatus},
            'ul_rssi': {'service_name': 'cambium_ul_rssi', 'model': ServiceStatus},
            'dl_rssi': {'service_name': 'cambium_dl_rssi', 'model': ServiceStatus},
        }
        technology = DeviceTechnology.objects.get(name='PMP').id
        devices_method_to_call = organization_customer_devices
        devices_method_kwargs = dict(specify_ptp_type='all')
        is_bh = False
        return data_source_config, technology, devices_method_to_call, devices_method_kwargs, is_bh


class PTP_Performance_Dashboard(PerformanceDashboardMixin, View):
    """
    The Class based View to get performance dashboard page requested.

    """
    template_name = 'rf_performance/ptp.html'

    def get_init_data(self):
        """
        Provide data for mixin's get method.
        """

        data_source_config = {
            'rssi': {'service_name': 'radwin_rssi', 'model': ServiceStatus},
            'uas': {'service_name': 'radwin_uas', 'model': ServiceStatus},
        }
        technology = DeviceTechnology.objects.get(name='P2P').id
        devices_method_to_call = organization_customer_devices
        devices_method_kwargs = dict(specify_ptp_bh_type='ss')
        is_bh = False
        return data_source_config, technology, devices_method_to_call, devices_method_kwargs, is_bh


class PTPBH_Performance_Dashboard(PerformanceDashboardMixin, View):
    """
    The Class based View to get performance dashboard page requested.

    """
    template_name = 'rf_performance/ptp_bh.html'

    def get_init_data(self):
        """
        Provide data for mixin's get method.
        """

        data_source_config = {
            'rssi': {'service_name': 'radwin_rssi', 'model': ServiceStatus},
            'availability': {'service_name': 'availability', 'model': NetworkAvailabilityDaily},
            'uas': {'service_name': 'radwin_uas', 'model': NetworkAvailabilityDaily},
        }
        technology = DeviceTechnology.objects.get(name='P2P').id
        devices_method_to_call = organization_network_devices
        devices_method_kwargs = dict(specify_ptp_bh_type='ss')
        is_bh = True
        return data_source_config, technology, devices_method_to_call, devices_method_kwargs, is_bh
