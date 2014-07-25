import json
import datetime
from django.db.models import Count
from django.db.models.query import ValuesQuerySet
from django.http import HttpResponse
from django.shortcuts import render_to_response, render
from django.views.generic import ListView
from django.views.generic.base import View
from django_datatables_view.base_datatable_view import BaseDatatableView
from device.models import Device, City, State, DeviceType
from inventory.models import SubStation, Circuit, Sector, BaseStation
from performance.models import PerformanceService, PerformanceNetwork
from service.models import ServiceDataSource, Service, DeviceServiceConfiguration
from operator import is_not
from functools import partial
from django.utils.dateformat import format

import logging
log=logging.getLogger(__name__)

SERVICE_DATA_SOURCE = {
    "uas": {"type" : "spline"},
    "rssi": {"type": "column"},
    "uptime": {"type": "spline"},
    "rta": {"type": "spline"},
    "pl": {"type": "column"}
}


class Live_Performance(ListView):

    model= PerformanceNetwork
    template_name = 'performance/live_perf.html'

    def get_context_data(self, **kwargs):
        context= super(Live_Performance, self).get_context_data(**kwargs)
        datatable_headers=[
            {'mData':'site_instance',      'sTitle' : 'Site ID',       'Width':'null', 'bSortable': False},
            {'mData':'id',                 'sTitle' : 'Device ID',     'sWidth':'null','sClass':'hidden-xs', 'bSortable': False},
            {'mData':'device_alias',       'sTitle' : 'Alias',         'sWidth':'null','sClass':'hidden-xs', 'bSortable': False},
            {'mData':'ip_address',         'sTitle' : 'IP',            'sWidth':'null','sClass':'hidden-xs', 'bSortable': False},
            {'mData':'device_type',        'sTitle' : 'Type',          'sWidth':'10%' ,'sClass':'hidden-xs', 'bSortable': False},
            {'mData':'city',               'sTitle' : 'City',          'sWidth':'null','sClass':'hidden-xs', 'bSortable': False},
            {'mData':'state',              'sTitle' : 'State',         'sWidth':'null','sClass':'hidden-xs', 'bSortable': False},
            {'mData':'packet_loss',        'sTitle' : 'Packet Loss',   'sWidth':'null','sClass':'hidden-xs', 'bSortable': False},
            {'mData':'latency',            'sTitle' : 'Latency',       'sWidth':'null','sClass':'hidden-xs', 'bSortable': False},
            {'mData':'last_updated',       'sTitle' : 'Last Updated',  'sWidth':'null','sClass':'hidden-xs', 'bSortable': False},
            {'mData':'actions',            'sTitle':'Actions',         'sWidth':'5%' ,'bSortable': False}
            ]

        context['datatable_headers'] = json.dumps(datatable_headers)
        context['page_type']=self.kwargs['page_type']
        return context


class LivePerformanceListing(BaseDatatableView):
    model = PerformanceNetwork
    columns = ['site_instance', 'id', 'device_alias', 'ip_address', 'device_type', 'city', 'state']

    def filter_queryset(self, qs):
        sSearch = self.request.GET.get('sSearch', None)
        if sSearch:
            result_list=list()
            for dictionary in qs:
                for key in dictionary.keys():
                    if sSearch.lower() in str(dictionary[key]).lower():
                        result_list.append(dictionary)
                        break
            return result_list
        return qs

    def get_initial_queryset(self):
        if not self.model:
            raise NotImplementedError("Need to provide a model or implement get_initial_queryset!")
        else:
            if self.request.user.userprofile.role.values_list('role_name', flat=True)[0] =='admin':
                organization_ids= list(self.request.user.userprofile.organization.get_children()\
                            .values_list('id', flat=True)) + [ self.request.user.userprofile.organization.id ]
            else:
                organization_ids= [self.request.user.userprofile.organization.id]

            if self.request.GET['page_type']=='customer':
                return self.get_initial_query_set_data( device_association='substation', organization_ids=organization_ids)

            elif self.request.GET['page_type'] == 'network':
                return self.get_initial_query_set_data(device_association='sector_configured_on', organization_ids=organization_ids)
            else:
                return []

    def get_initial_query_set_data(self, device_association='', **kwargs):
        device_list=list()
        devices= Device.objects.filter( organization__in= kwargs['organization_ids']).values(*self.columns+ \
                                                                        ['device_name', device_association])

        required_devices = []

        for device in devices:
            if device[device_association]:
                required_devices.append(device["device_name"])

        query = prepare_query(table_name="performance_performancenetwork",
                              devices=required_devices,
                              data_sources=["pl", "rta"]
                              )
        performance_data = PerformanceNetwork.objects.raw(query)

        for device in devices:
            if device[device_association]:
                device.update({
                    "packet_loss": "",
                    "latency": "",
                    "last_updated": "",
                    "city": City.objects.get(id=device['city']).city_name,
                    "state": State.objects.get(id=device['state']).state_name,
                    "device_type": DeviceType.objects.get(pk=int(device['device_type'])).name
                })
                for data in performance_data:
                    if str(data.device_name).strip().lower() == str(device["device_name"]).strip().lower():
                        d_src = str(data.data_source).strip().lower()
                        current_val = str(data.current_value)
                        if d_src == "pl":
                            device["packet_loss"] = current_val
                        if d_src == "rta":
                            device["latency"] = current_val
                        device["last_updated"] = str(datetime.datetime.fromtimestamp(float( data.sys_timestamp )))
                        device_list.append(device)

        return device_list

    def prepare_results(self, qs):
        if qs:
            for dct in qs:
                if self.request.GET['page_type']=='customer':
                    substation_id=Device.objects.get(id=dct['id']).substation_set.values()[0]['id']
                    dct.update(actions='<a href="/performance/{0}_live/{1}/"><i class="fa fa-list-alt text-info"></i></a>'\
                               .format( self.request.GET['page_type'], substation_id))
                elif self.request.GET['page_type'] == 'network':
                    dct.update(actions='<a href="/performance/{0}_live/{1}/"><i class="fa fa-list-alt text-info"></i></a>'\
                               .format( self.request.GET['page_type'], dct['id']))

        return qs

    def get_context_data(self, *args, **kwargs):
        request = self.request
        self.initialize(*args, **kwargs)

        qs = self.get_initial_queryset()

        # number of records before filtering
        total_records = len(qs)


        # number of records after filtering
        total_display_records = len(qs)

        # qs = self.ordering(qs)
        qs = self.paging(qs)
        #if the qs is empty then JSON is unable to serialize the empty ValuesQuerySet.Therefore changing its type to list.
        if not qs and isinstance(qs, ValuesQuerySet):
            qs=list(qs)

        # prepare output data
        qs = self.prepare_results(qs)
        aaData = self.filter_queryset(qs)
        ret = {'sEcho': int(request.REQUEST.get('sEcho', 0)),
               'iTotalRecords': total_records,
               'iTotalDisplayRecords': total_display_records,
               'aaData': aaData
               }
        return ret

class Get_Perfomance(View):

    def get(self, request, page_type = "no_page", device_id=0):
        page_data = {
                        'page_title' : page_type.capitalize(),
                        'device_id' : device_id,
                        'get_devices_url' : 'performance/get_inventory_devices/'+str(page_type),
                        'get_status_url' : 'performance/get_inventory_device_status/'+str(page_type)+'/device/'+str(device_id),
                        'get_services_url' : 'performance/get_inventory_service_data_sources/'+str(page_type)+'/device/'+str(device_id),
                    }

        return render(request, 'performance/single_device_perf.html',page_data)

class Performance_Dashboard(View):

    def get(self, request):
        return render_to_response('performance/perf_dashboard.html')


class Sector_Dashboard(View):

    def get(self, request):
        return render(request, 'performance/sector_dashboard.html')


class Fetch_Inventory_Devices(View):

    def get(self, request, page_type=None):

        result={
            'success' : 0,
            'message' : 'Substation Devices Not Fetched Successfully.',
            'data' : {
                'meta' : {},
                'objects' : []
            }
        }

        logged_in_user= request.user.userprofile

        if 'admin' in logged_in_user.role.values_list('role_name', flat=True):
            organizations= logged_in_user.organization.get_descendants(include_self=True)
            for organization in organizations:
                result['data']['objects']+= self.get_result(page_type, organization)
        else:
            organization= logged_in_user.organization
            result['data']['objects']+= self.get_result(page_type, organization)

        result['success']=1
        result['message']='Substation Devices Fetched Successfully.'
        return HttpResponse(json.dumps(result))

    def get_result(self, page_type, organization):

        if page_type == "customer":
            substation_result= self.organization_devices_substations(organization)
            return substation_result
        elif page_type == "network":
            basestation_result = self.organization_devices_basestations(organization)
            return basestation_result

    def organization_devices_substations(self, organization):
        #To result back the all the substations from the given organization as an argument.
        organization_substations= SubStation.objects.filter(device__in = Device.objects.filter(organization= organization.id).\
                                  values_list('id', flat=True)).values_list('id', 'name', 'alias')
        result=list()
        for substation in organization_substations:
            result.append({ 'id':substation[0], 'name':substation[1], 'alias':substation[2] })

        return result

    def organization_devices_basestations(self, organization):
        #To result back the all the basestations from the given organization as an argument.
        sector_configured_on_devices_list= Sector.objects.filter( sector_configured_on__id__in= organization.device_set.\
                values_list('id', flat=True)).values_list('sector_configured_on').annotate(dcount=Count('base_station'))

        sector_configured_on_devices_ids= map(lambda x: x[0], sector_configured_on_devices_list)
        sector_configured_on_devices= Device.objects.filter(id__in= sector_configured_on_devices_ids)
        result=list()
        for sector_configured_on_device in sector_configured_on_devices:
            result.append({ 'id':sector_configured_on_device.id, 'name':sector_configured_on_device.device_name,
                            'alias':sector_configured_on_device.device_alias })

        return result


class Inventory_Device_Status(View):

    def get(self, request, page_type, device_id):
        result={
            'success' : 0,
            'message' : 'Inventory Device Status Not Fetched Successfully.',
            'data' : {
                'meta' : {},
                'objects' : {}
            }
        }
        result['data']['objects']['values']=list()
        if page_type =='customer':

            substation= SubStation.objects.get(id=device_id)
            substation_device= Device.objects.get(id= substation.device_id)
            sector= Circuit.objects.get(sub_station= substation.id).sector
            base_station= BaseStation.objects.get(id= Sector.objects.get(id=sector.id).base_station.id)
            result['data']['objects']['headers']= ['BS Name', 'SSName','Building Height', 'Tower Height',
                                                   'City', 'State', 'IP Address', 'MAC Address']
            result['data']['objects']['values']= [ base_station.name, substation.name,
                                                   substation.building_height, substation.tower_height,
                                                   City.objects.get(id=substation.city).city_name,
                                                   State.objects.get(id=substation.state).state_name,
                                                   substation_device.ip_address,
                                                   substation_device.mac_address ]

        elif page_type =='network':

            # base_station= BaseStation.objects.get(id=device_id)
            # sector_configured_on_device= Sector.objects.filter(base_station= base_station.id).values_list('sector_configured_on', flat=True)
            sector_configured_on_device= Device.objects.get(id=int(device_id))
            result['data']['objects']['headers']= ['BS Name','Building Height', 'Tower Height',
                                                   'City', 'State', 'IP Address', 'MAC Address']
            base_station_list= Sector.objects.filter(sector_configured_on= sector_configured_on_device.id).values_list('base_station', flat=True)
            if base_station_list:
                base_station=BaseStation.objects.get(id=base_station_list[0])
                result['data']['objects']['values']= [ base_station.name, base_station.building_height, base_station.tower_height,
                                                       City.objects.get(id=base_station.city).city_name,
                                                       State.objects.get(id=base_station.state).state_name,
                                                       sector_configured_on_device.ip_address,
                                                       sector_configured_on_device.mac_address ]

        result['data']['objects']['values']=map(lambda val : val if val else 'N/A', result['data']['objects']['values'])
        result['success']=1
        result['message']='Inventory Device Status Fetched Successfully.'
        return HttpResponse(json.dumps(result))


class Inventory_Device_Service_Data_Source(View):

    def get(self, request, page_type, device_id):

        result={
            'success' : 0,
            'message' : 'Substation Devices Services Data Source Not Fetched Successfully.',
            'data' : {
                'meta' : {},
                'objects' : []
            }
        }
        inventory_device_type_id=None
        if page_type =='customer':
            inventory_device= SubStation.objects.get(id= device_id)
            inventory_device_type_id= Device.objects.get(id= inventory_device.device_id).device_type

        elif page_type == 'network':
            #for basestation we need to fetch sector_configured_on device field from the device
            inventory_device_type_id= Device.objects.get(id=int(device_id)).device_type

        #first check for the service configuration table
        inventory_device_service_name = DeviceServiceConfiguration.objects.\
            filter(device_name=Device.objects.get(id=int(device_id)).device_name).\
            values_list('service_name', flat=True)

        if not len(inventory_device_service_name):
            inventory_device_service_name= DeviceType.objects.get(id= inventory_device_type_id) \
                .service.values_list('name', flat=True)

        ##also append PD and RTA as latency and packet drop

        result['data']['objects'].append({
                'name':"rta",
                'title':"Latency",
                #@TODO: all the ursl must end with a / - django style
                'url':'performance/service/ping/service_data_source/rta/'+page_type+'/device/'+str(device_id),
                'active':0
            })

        result['data']['objects'].append({
                'name':"pl",
                'title':"Packet Drop",
                #@TODO: all the ursl must end with a / - django style
                'url':'performance/service/ping/service_data_source/pl/'+page_type+'/device/'+str(device_id),
                'active':0
            })

        for service_name in inventory_device_service_name:
            service_data_sources= Service.objects.get(name= service_name).service_data_sources.all()
            for service_data_source in service_data_sources:
                result['data']['objects'].append({
                    'name':service_data_source.name,
                    'title':service_data_source.alias +' ('+service_name+')',
                    #@TODO: all the ursl must end with a / - django style
                    'url':'performance/service/'+service_name+'/service_data_source/'+ service_data_source.name +'/'+page_type+'/device/'+str(device_id),
                    'active':0
                })

        result['success']=1
        result['message']='Substation Devices Services Data Source Fetched Successfully.'
        return HttpResponse(json.dumps(result))


class Get_Service_Type_Performance_Data(View):

    def get(self, request, page_type, service_name, service_data_source_type, device_id):
        result={
        'success' : 0,
        'message' : 'Substation Service Not Fetched Successfully.',
        'data' : {
            'meta' : {},
            'objects' : {}
            }
        }
        inventory_device_name=None
        if page_type =='customer':
            inventory_device_name= SubStation.objects.get(id= int(device_id)).device.device_name
        elif page_type == 'network':
            inventory_device_name=Device.objects.get(id=int(device_id)).device_name
        #raw query commented.
        # performance_data=PerformanceService.objects.raw('select id, max(id), avg_value, sys_timestamp from \
        #                 performance_performanceservice where data_source= {0} and device_name= {1} \
        #                 group by sys_timestamp order by id desc limit 6;'.format(service_data_source_type, substation_name))

        now=format(datetime.datetime.now(),'U')
        now_minus_60_min=format(datetime.datetime.now() + datetime.timedelta(minutes=-60), 'U')

        if service_data_source_type in ['pl', 'rta']:

            performance_data=PerformanceNetwork.objects.filter(device_name=inventory_device_name,
                                                                service_name=service_name,
                                                                data_source=service_data_source_type,
                                                                sys_timestamp__gte=now_minus_60_min,
                                                                sys_timestamp__lte=now)
            # log.info("network performance data %s device name" %(performance_data, inventory_device_name))
        else:
            performance_data=PerformanceService.objects.filter(device_name=inventory_device_name,
                                                               service_name=service_name,
                                                               data_source=service_data_source_type,
                                                               sys_timestamp__gte=now_minus_60_min,
                                                               sys_timestamp__lte=now)

        if performance_data:
            data_list=[]
            warn_data_list=[]
            crit_data_list=[]
            aggregate_data = {}
            for data in performance_data:
                temp_time = data.sys_timestamp

                if temp_time in aggregate_data:
                    continue
                else:
                    aggregate_data[temp_time] = data.sys_timestamp
                    result['data']['objects']['type']= SERVICE_DATA_SOURCE[str(data.data_source).lower()]["type"] if \
                        data.data_source in SERVICE_DATA_SOURCE else "spline"
                    #data_list.append([data.sys_timestamp, data.avg_value ])

                    data_list.append([data.sys_timestamp*1000, float(data.avg_value) if data.avg_value else 0])

                    warn_data_list.append([data.sys_timestamp*1000, float(data.warning_threshold)
                                                                    if data.critical_threshold else None])

                    crit_data_list.append([data.sys_timestamp*1000, float(data.critical_threshold)
                                                                    if data.critical_threshold else None])

                    result['success']=1
                    result['message']='Device Performance Data Fetched Successfully.'
                    result['data']['objects']['chart_data']=[{'name': str(data.data_source).upper(),
                                                              'color': '#70AFC4',
                                                              'data': data_list,
                                                              'type': result['data']['objects']['type']
                                                              },
                                                             {'name': str("warning threshold").title(),
                                                              'color': '#FFE90D',
                                                              'data': warn_data_list,
                                                              'type': 'line'
                                                            },
                                                             {'name': str("critical threshold").title(),
                                                              'color': '#FF193B',
                                                              'data': crit_data_list,
                                                              'type': 'line'
                                                             }
                    ]

        return HttpResponse(json.dumps(result), mimetype="application/json")

###to draw each data point w.r.t threshold we would need to use the following
# compare_point = lambda p1, p2, p3: '#70AFC4' if p1 < p2 else ('#FFE90D' if p2 < p1 <p3 else '#FF193B')
# if data.avg_value:
#     formatter_data_point = {
#         "name": str(data.data_source).upper(),
#         "color": compare_point(float(data.avg_value),
#                                float(data.warning_threshold),
#                                float(data.critical_threshold)
#         ),
#         "y": float(data.avg_value),
#         "x": data.sys_timestamp*1000
#     }
# else:
#     formatter_data_point = {
#         "name": str(data.data_source).upper(),
#         "color": '#70AFC4',
#         "y": None,
#         "x": data.sys_timestamp*1000
#     }
#this ensures a further good presentation of data w.r.t thresholds
#

#misc utility functions

def prepare_query(table_name=None, devices=None, data_sources=["pl","rta"]):
    in_string = lambda x: "'"+str(x)+"'"
    query = None
    if table_name and devices:
        query = "SELECT * FROM `{0}` " \
            "WHERE `{0}`.`device_name` in ( {1} ) " \
            "AND `{0}`.`data_source` in ('pl', 'rta') " \
            "GROUP BY `{0}`.`device_name`, `{0}`.`data_source`" \
            "ORDER BY `{0}`.sys_timestamp DESC" \
            .format(table_name, (",".join(map(in_string, devices))), (',').join(map(in_string, data_sources)))

    return query