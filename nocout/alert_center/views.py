import json
import time
from django.db.models.query import ValuesQuerySet
from django.shortcuts import render_to_response
from django.views.generic import ListView
from django.views.generic.base import View
from django.template import RequestContext
from django_datatables_view.base_datatable_view import BaseDatatableView
from performance.models import PerformanceMetric

# Create your views here.

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
class LatencyList(ListView):
    model = PerformanceMetric
    template_name = 'alert_center/network_alerts_list.html'

    def get_context_data(self, **kwargs):
        context=super(LatencyList, self).get_context_data(**kwargs)
        datatable_headers_latency = [
            {'mData':'device_name',                    'sTitle' : 'Device Name',                 'sWidth':'null',},
            {'mData':'service_name',                   'sTitle' : 'Service Name',                'sWidth':'null',},
            {'mData':'machine_name',                   'sTitle' : 'Machine Name',           'sWidth':'null','sClass':'hidden-xs'},
            {'mData':'site_name',                      'sTitle' : 'Site Name',               'sWidth':'null',},
            {'mData':'data_source',                    'sTitle' : 'Data Source',             'sWidth':'null','sClass':'hidden-xs'},
            {'mData':'avg_value',                      'sTitle' : 'Latency',             'sWidth':'null','sClass':'hidden-xs'},
            {'mData':'check_timestamp',                'sTitle' : 'Timestamp',          'sWidth':'null',},
            ]
        datatable_headers_packetdrop = [
            {'mData':'device_name',                    'sTitle' : 'Device Name',                 'sWidth':'null',},
            {'mData':'service_name',                   'sTitle' : 'Service Name',                'sWidth':'null',},
            {'mData':'machine_name',              'sTitle' : 'Machine Name',           'sWidth':'null','sClass':'hidden-xs'},
            {'mData':'site_name',                  'sTitle' : 'Site Name',               'sWidth':'null',},
            {'mData':'data_source',                    'sTitle' : 'Data Source',             'sWidth':'null','sClass':'hidden-xs'},
            {'mData':'avg_value',                'sTitle' : 'PacketDrop',             'sWidth':'null','sClass':'hidden-xs'},
            {'mData':'check_timestamp',             'sTitle' : 'Timestamp',          'sWidth':'null',},
            ]
        context['datatable_headers_packetdrop'] = json.dumps(datatable_headers_packetdrop)
        context['datatable_headers_latency'] = json.dumps(datatable_headers_latency)
        return context

class LatencyListingTable(BaseDatatableView):
    model = PerformanceMetric
    columns = ['device_name', 'service_name', 'machine_name', 'site_name', 'data_source', 'avg_value', 'check_timestamp']
    order_columns = ['device_name', 'service_name', 'machine_name', 'site_name', 'data_source', 'avg_value', 'check_timestamp']

    def filter_queryset(self, qs):
        sSearch = self.request.GET.get('sSearch', None)
        ##TODO:Need to optimise with the query making login.
        if sSearch:
            query=[]
            exec_query = "qs = %s.objects.filter("%(self.model.__name__)
            for column in self.columns[:-1]:
                query.append("Q(%s__contains="%column + "\"" +sSearch +"\"" +")")

            exec_query += " | ".join(query)
            exec_query += ").values(*"+str(self.columns+['id'])+")"
            # qs=qs.filter( reduce( lambda q, column: q | Q(column__contains=sSearch), self.columns, Q() ))
            # qs = qs.filter(Q(username__contains=sSearch) | Q(first_name__contains=sSearch) | Q() )
            exec exec_query

        return qs

    def get_initial_queryset(self):
        if not self.model:
            raise NotImplementedError("Need to provide a model or implement get_initial_queryset!")
        return PerformanceMetric.objects.filter(data_source='rta').values(*self.columns+['id'])

    def prepare_results(self, qs):
        if qs:
            qs = [ { key: val if val else "" for key, val in dct.items() } for dct in qs ]
        for dct in qs:
            dct['check_timestamp'] =  time.strftime('%a %d-%b-%Y %H:%M:%S %Z', time.localtime(dct['check_timestamp']))
            dct.update(actions='<a href="/circuit/edit/{0}"><i class="fa fa-pencil text-dark"></i></a>\
                <a href="/circuit/delete/{0}"><i class="fa fa-trash-o text-danger"></i></a>'.format(dct.pop('id')))
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
    
    
#**************************************** PacketDrop *********************************************
class PacketDropListingTable(BaseDatatableView):
    model = PerformanceMetric
    columns = ['device_name', 'service_name', 'machine_name', 'site_name', 'data_source', 'avg_value', 'check_timestamp']
    order_columns = ['device_name', 'service_name', 'machine_name', 'site_name', 'data_source', 'avg_value', 'check_timestamp']

    def filter_queryset(self, qs):
        sSearch = self.request.GET.get('sSearch', None)
        ##TODO:Need to optimise with the query making login.
        if sSearch:
            query=[]
            exec_query = "qs = %s.objects.filter("%(self.model.__name__)
            for column in self.columns[:-1]:
                query.append("Q(%s__contains="%column + "\"" +sSearch +"\"" +")")

            exec_query += " | ".join(query)
            exec_query += ").values(*"+str(self.columns+['id'])+")"
            # qs=qs.filter( reduce( lambda q, column: q | Q(column__contains=sSearch), self.columns, Q() ))
            # qs = qs.filter(Q(username__contains=sSearch) | Q(first_name__contains=sSearch) | Q() )
            exec exec_query

        return qs

    def get_initial_queryset(self):
        if not self.model:
            raise NotImplementedError("Need to provide a model or implement get_initial_queryset!")
        return PerformanceMetric.objects.filter(data_source='pl').values(*self.columns+['id'])

    def prepare_results(self, qs):
        if qs:
            qs = [ { key: val if val else "" for key, val in dct.items() } for dct in qs ]
        for dct in qs:
            dct['check_timestamp'] =  time.strftime('%a %d-%b-%Y %H:%M:%S %Z', time.localtime(dct['check_timestamp']))
            dct.update(actions='<a href="/circuit/edit/{0}"><i class="fa fa-pencil text-dark"></i></a>\
                <a href="/circuit/delete/{0}"><i class="fa fa-trash-o text-danger"></i></a>'.format(dct.pop('id')))
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