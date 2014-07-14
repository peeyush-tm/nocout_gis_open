import json
import logging
import time
import datetime
from django.db.models.query import ValuesQuerySet
from django.shortcuts import render_to_response
from django.views.generic import ListView
from django.views.generic.base import View
from django.template import RequestContext
from django_datatables_view.base_datatable_view import BaseDatatableView
from device.models import Device
from performance.models import PerformanceNetwork, EventNetwork, EventService

logger=logging.getLogger(__name__)

def getNetworkAlert(request):

    return render_to_response('alert_center/network_alerts_list.html',context_instance=RequestContext(request))

def getCustomerAlert(request, page_type = "default_device_name"):

    if(page_type == "latency"):
        return render_to_response('alert_center/customer_latency_alerts_list.html',context_instance=RequestContext(request))
    else:
        return render_to_response('alert_center/customer_packet_alerts_list.html',context_instance=RequestContext(request))

def getCustomerAlertDetail(request):

    return render_to_response('alert_center/customer_details_list.html',context_instance=RequestContext(request))

def getNetworkAlertDetail(request):

    return render_to_response('alert_center/network_details_list.html',context_instance=RequestContext(request))


#**************************************** Latency *********************************************
class AlertCenterNetworkListing(ListView):
    model = PerformanceNetwork
    template_name = 'alert_center/network_alerts_list.html'

    def get_context_data(self, **kwargs):
        context=super(AlertCenterNetworkListing, self).get_context_data(**kwargs)
        datatable_headers_latency = [
            {'mData':'device_name',                'sTitle' : 'Device Name',            'sWidth':'null',},
            {'mData':'service_name',               'sTitle' : 'Service Name',           'sWidth':'null',},
            {'mData':'machine_name',               'sTitle' : 'Machine Name',           'sWidth':'null','sClass':'hidden-xs'},
            {'mData':'site_name',                  'sTitle' : 'Site Name',              'sWidth':'null',},
            {'mData':'ip_address',                 'sTitle' : 'IP Address',             'sWidth':'null','sClass':'hidden-xs'},
            {'mData':'severity',                   'sTitle' : 'Severity',               'sWidth':'null','sClass':'hidden-xs'},
            {'mData':'data_source',                'sTitle' : 'Data Source',            'sWidth':'null','sClass':'hidden-xs'},
            {'mData':'avg_value',                  'sTitle' : 'Latency',                'sWidth':'null','sClass':'hidden-xs'},
            {'mData':'sys_timestamp',              'sTitle' : 'Timestamp',              'sWidth':'null',},]

        datatable_headers_packetdrop = [
            {'mData':'device_name',                'sTitle' : 'Device Name',            'sWidth':'null',},
            {'mData':'service_name',               'sTitle' : 'Service Name',           'sWidth':'null',},
            {'mData':'machine_name',               'sTitle' : 'Machine Name',           'sWidth':'null','sClass':'hidden-xs'},
            {'mData':'site_name',                  'sTitle' : 'Site Name',              'sWidth':'null',},
            {'mData':'ip_address',                 'sTitle' : 'IP Address',             'sWidth':'null','sClass':'hidden-xs'},
            {'mData':'severity',                   'sTitle' : 'Severity',               'sWidth':'null','sClass':'hidden-xs'},
            {'mData':'data_source',                'sTitle' : 'Data Source',            'sWidth':'null','sClass':'hidden-xs'},
            {'mData':'avg_value',                  'sTitle' : 'Latency',                'sWidth':'null','sClass':'hidden-xs'},
            {'mData':'sys_timestamp',              'sTitle' : 'Timestamp',              'sWidth':'null',},
            ]
        # datatable_headers_down = [
        #     {'mData':'device_name',                'sTitle' : 'Device Name',            'sWidth':'null',},
        #     {'mData':'service_name',               'sTitle' : 'Service Name',           'sWidth':'null',},
        #     {'mData':'machine_name',               'sTitle' : 'Machine Name',           'sWidth':'null','sClass':'hidden-xs'},
        #     {'mData':'site_name',                  'sTitle' : 'Site Name',              'sWidth':'null',},
        #     {'mData':'ip_address',                 'sTitle' : 'IP Address',             'sWidth':'null','sClass':'hidden-xs'},
        #     {'mData':'severity',                   'sTitle' : 'Severity',               'sWidth':'null','sClass':'hidden-xs'},
        #     {'mData':'data_source',                'sTitle' : 'Data Source',            'sWidth':'null','sClass':'hidden-xs'},
        #     {'mData':'avg_value',                  'sTitle' : 'Latency',                'sWidth':'null','sClass':'hidden-xs'},
        #     {'mData':'check_timestamp',            'sTitle' : 'Timestamp',              'sWidth':'null',},
        #     {'mData':'description',          'sTitle' : 'Event Description',      'sWidth':'null',},
        #     ]
        # datatable_headers_servicealerts = [
        #     {'mData':'device_name',                'sTitle' : 'Device Name',            'sWidth':'null',},
        #     {'mData':'service_name',               'sTitle' : 'Service Name',           'sWidth':'null',},
        #     {'mData':'machine_name',               'sTitle' : 'Machine Name',           'sWidth':'null','sClass':'hidden-xs'},
        #     {'mData':'site_name',                  'sTitle' : 'Site Name',              'sWidth':'null',},
        #     {'mData':'ip_address',                 'sTitle' : 'IP Address',             'sWidth':'null','sClass':'hidden-xs'},
        #     {'mData':'severity',                   'sTitle' : 'Severity',               'sWidth':'null','sClass':'hidden-xs'},
        #     {'mData':'data_source',                'sTitle' : 'Data Source',            'sWidth':'null','sClass':'hidden-xs'},
        #     {'mData':'avg_value',                  'sTitle' : 'Latency',                'sWidth':'null','sClass':'hidden-xs'},
        #     {'mData':'check_timestamp',            'sTitle' : 'Timestamp',              'sWidth':'null',},
        #     {'mData':'description',          'sTitle' : 'Event Description',      'sWidth':'null',},
        #     ]
        # context['datatable_headers_servicealerts'] = json.dumps(datatable_headers_servicealerts)
        # context['datatable_headers_down'] = json.dumps(datatable_headers_down)
        context['datatable_headers_packetdrop'] = json.dumps(datatable_headers_packetdrop)
        context['datatable_headers_latency'] = json.dumps(datatable_headers_latency)
        return context

class AlertCenterNetworkListingTable(BaseDatatableView):
    model = PerformanceNetwork
    columns = ['device_name', 'service_name', 'machine_name', 'site_name', 'ip_address', 'severity', 'data_source', 'avg_value', 'sys_timestamp']
    order_columns = ['device_name', 'service_name', 'machine_name', 'site_name', 'ip_address', 'severity', 'data_source', 'avg_value', 'sys_timestamp']

    def filter_queryset(self, qs):

        sSearch = self.request.GET.get('sSearch', None)
        if sSearch:
            result_list=list()
            for dictionary in qs:
                for key in dictionary.keys():
                    if str(dictionary[key])==sSearch:
                        result_list.append(dictionary)

            return result_list

        return qs

    def get_initial_queryset(self):
        if not self.model:
            raise NotImplementedError("Need to provide a model or implement get_initial_queryset!")

        if self.request.user.userprofile.role.values_list('role_name', flat=True)[0] =='admin':
            organization_ids= self.request.user.userprofile.organization.get_descendants(include_self= True)\
                                                                             .values_list('id', flat= True)
        else:
            organization_ids= [ self.request.user.userprofile.organization.id ]

        devices= Device.objects.filter( organization__in= organization_ids)
        device_list=list()
        performance_data=list()
        for device in devices:
            if device.sector_configured_on.all():
                if 'latency' in self.request.path_info:
                    performance_data= PerformanceNetwork.objects.raw('''select * from performance_performancenetwork  \
                                       where id = (select MAX(id) from performance_performancenetwork where \
                                        (device_name=%s and data_source=%s))''' ,[ device.device_name, 'rta'])

                elif 'packetdrop' in self.request.path_info:

                    performance_data= PerformanceNetwork.objects.raw('''select * from performance_performancenetwork  \
                                      where id = (select MAX(id) from performance_performancenetwork where  \
                                      (device_name=%s and data_source=%s))''' ,[ device.device_name, 'pl'])
                for data in performance_data:
                    device_list.append({
                        'device_name' : data.device_name,
                        'service_name':data.service_name,
                        'machine_name':data.machine_name,
                        'site_name':data.site_name,
                        'ip_address':data.ip_address,
                        'severity':data.severity,
                        'data_source':data.data_source,
                        'avg_value':data.avg_value,
                        'sys_timestamp':str(datetime.datetime.fromtimestamp(float( data.sys_timestamp )))
                    })

        return device_list

    def prepare_results(self, qs):
        if qs:
            qs = [ { key: val if val else "" for key, val in dct.items() } for dct in qs ]
        return qs

    def get_context_data(self, *args, **kwargs):
        request = self.request
        self.initialize(*args, **kwargs)

        qs = self.get_initial_queryset()

        # number of records before filtering
        total_records = len(qs)

        qs = self.filter_queryset(qs)

        # number of records after filtering
        total_display_records = len(qs)

        # qs = self.ordering(qs)
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
    
class CustomerAlertList(ListView):
    model = PerformanceNetwork
    template_name = 'alert_center/customer_alerts_list.html'

    def get_context_data(self, **kwargs):
        context=super(CustomerAlertList, self).get_context_data(**kwargs)
        datatable_headers = [
            {'mData':'device_name',                'sTitle' : 'Device Name',            'sWidth':'null',},
            {'mData':'service_name',               'sTitle' : 'Service Name',           'sWidth':'null',},
            {'mData':'machine_name',               'sTitle' : 'Machine Name',           'sWidth':'null','sClass':'hidden-xs'},
            {'mData':'site_name',                  'sTitle' : 'Site Name',              'sWidth':'null',},
            {'mData':'ip_address',                 'sTitle' : 'IP Address',             'sWidth':'null','sClass':'hidden-xs'},
            {'mData':'severity',                   'sTitle' : 'Severity',               'sWidth':'null','sClass':'hidden-xs'},
            {'mData':'data_source',                'sTitle' : 'Data Source',            'sWidth':'null','sClass':'hidden-xs'},
            {'mData':'avg_value',                  'sTitle' : 'Latency',                'sWidth':'null','sClass':'hidden-xs'},
            {'mData':'sys_timestamp',              'sTitle' : 'Timestamp',              'sWidth':'null',},
            ]
        context['datatable_headers'] = json.dumps(datatable_headers)
        context['data_source'] = " ".join(self.kwargs['data_source'].split('_')).title()
        return context

class CustomerAlertListingTable(BaseDatatableView):
    model = PerformanceNetwork
    columns = ['device_name', 'service_name', 'machine_name', 'site_name', 'ip_address', 'severity', 'data_source', 'avg_value', 'sys_timestamp']
    order_columns = ['device_name', 'service_name', 'machine_name', 'site_name', 'ip_address', 'severity', 'data_source', 'avg_value', 'sys_timestamp']

    def filter_queryset(self, qs):

        sSearch = self.request.GET.get('sSearch', None)
        if sSearch:
            result_list=list()
            for dictionary in qs:
                for key in dictionary.keys():
                    if str(dictionary[key])==sSearch:
                        result_list.append(dictionary)

            return result_list

        return qs

    def get_initial_queryset(self):
        if not self.model:
            raise NotImplementedError("Need to provide a model or implement get_initial_queryset!")

        if self.request.user.userprofile.role.values_list('role_name', flat=True)[0] =='admin':
            organization_ids= self.request.user.userprofile.organization.get_descendants(include_self= True)\
                                                                             .values_list('id', flat= True)
        else:
            organization_ids= [ self.request.user.userprofile.organization.id ]

        devices= Device.objects.filter( organization__in= organization_ids)
        device_list=list()
        performance_data=list()
        for device in devices:
            if device.substation_set.all():
                if self.request.GET['data_source'] == 'latency':
                    performance_data= PerformanceNetwork.objects.raw('''select * from performance_performancenetwork  \
                                       where id = (select MAX(id) from performance_performancenetwork where \
                                        (device_name=%s and data_source=%s))''' ,[ device.device_name, 'rta'])

                elif self.request.GET['data_source'] == 'packet_drop':

                    performance_data= PerformanceNetwork.objects.raw('''select * from performance_performancenetwork  \
                                      where id = (select MAX(id) from performance_performancenetwork where  \
                                      (device_name=%s and data_source=%s))''' ,[ device.device_name, 'pl'])
                for data in performance_data:
                    device_list.append({
                        'device_name' : data.device_name,
                        'service_name':data.service_name,
                        'machine_name':data.machine_name,
                        'site_name':data.site_name,
                        'ip_address':data.ip_address,
                        'severity':data.severity,
                        'data_source':data.data_source,
                        'avg_value':data.avg_value,
                        'sys_timestamp':str(datetime.datetime.fromtimestamp(float( data.sys_timestamp )))
                    })

        return device_list

    def prepare_results(self, qs):
        if qs:
            qs = [ { key: val if val else "" for key, val in dct.items() } for dct in qs ]
        return qs

    def get_context_data(self, *args, **kwargs):
        request = self.request
        self.initialize(*args, **kwargs)

        qs = self.get_initial_queryset()

        # number of records before filtering
        total_records = len(qs)

        qs = self.filter_queryset(qs)

        # number of records after filtering
        total_display_records = len(qs)

        # qs = self.ordering(qs)
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

