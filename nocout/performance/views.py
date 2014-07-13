import json
import datetime
from django.db.models import Count
from django.db.models.query import ValuesQuerySet
from django.http import HttpResponse
from django.shortcuts import render_to_response, render
from django.views.generic import ListView
from django.views.generic.base import View
from django.template import RequestContext

# Create your views here.
from django_datatables_view.base_datatable_view import BaseDatatableView
from device.models import Device, City, State, DeviceType

from inventory.models import SubStation, Circuit, Sector, BaseStation
from performance.models import PerformanceService
from service.models import Service, ServiceDataSource
from operator import is_not
from functools import partial
from django.utils.dateformat import format

class Live_Performance(ListView):

    model= PerformanceService
    template_name = 'performance/live_perf.html'

    def get_context_data(self, **kwargs):
        context= super(Live_Performance, self).get_context_data(**kwargs)
        datatable_headers=[
            {'mData':'site_instance',      'sTitle' : 'Site ID',       'Width':'null',},
            {'mData':'id',                 'sTitle' : 'Device ID',     'sWidth':'null','sClass':'hidden-xs'},
            {'mData':'device_alias',       'sTitle' : 'Alias',         'sWidth':'null','sClass':'hidden-xs'},
            {'mData':'ip_address',         'sTitle' : 'IP',            'sWidth':'null','sClass':'hidden-xs'},
            {'mData':'device_type',        'sTitle' : 'Type',          'sWidth':'10%' ,'sClass':'hidden-xs'},
            {'mData':'city',               'sTitle' : 'City',          'sWidth':'null','sClass':'hidden-xs'},
            {'mData':'state',              'sTitle' : 'State',         'sWidth':'null','sClass':'hidden-xs'},
            {'mData':'packet_loss',        'sTitle' : 'Packet Loss',   'sWidth':'null','sClass':'hidden-xs'},
            {'mData':'latency',            'sTitle' : 'Latency',       'sWidth':'null','sClass':'hidden-xs'},
            {'mData':'last_updated',       'sTitle' : 'Last Updated',  'sWidth':'null','sClass':'hidden-xs'},
            ]

        context['datatable_headers'] = json.dumps(datatable_headers)
        context['page_type']=self.kwargs['page_type']
        return context


class LivePerformanceListing(BaseDatatableView):
    model = PerformanceService
    columns = ['site_instance', 'id', 'device_alias', 'ip_address', 'device_type', 'city', 'state']
    order_columns = ['site_instance', 'device_id', 'alias', 'ip', 'device_type', 'city', 'state']

    def filter_queryset(self, qs):
        # sSearch = self.request.GET.get('sSearch', None)
        # ##TODO:Need to optimise with the query making login.
        # if sSearch:
        #     query=[]
        #     exec_query = "qs = %s.objects.filter("%(self.model.__name__)
        #     for column in self.columns[:-1]:
        #         query.append("Q(%s__contains="%column + "\"" +sSearch +"\"" +")")
        #
        #     exec_query += " | ".join(query)
        #     exec_query += ").values(*"+str(self.columns+['id'])+")"
        #     # qs=qs.filter( reduce( lambda q, column: q | Q(column__contains=sSearch), self.columns, Q() ))
        #     # qs = qs.filter(Q(username__contains=sSearch) | Q(first_name__contains=sSearch) | Q() )
        #     exec exec_query
        return qs

    def get_initial_queryset(self):
        if not self.model:
            raise NotImplementedError("Need to provide a model or implement get_initial_queryset!")
        else:
            if self.request.user.userprofile.role.values_list('role_name', flat=True)[0] =='admin':
                organization_ids= self.request.user.userprofile.organization.get_descendants(include_self= True)\
                                                                             .values_list('id', flat= True)
            else:
                organization_ids= [self.request.user.userprofile.organization.id]

            if self.request.GET['page_type']=='customer':
                return self.get_initial_query_set_data( device_association='substation', organization_ids=organization_ids)

            elif self.request.GET['page_type'] == 'network':
                return self.get_initial_query_set_data(device_association='sector_configured_on', organization_ids=organization_ids)
            else:
                return self.get_initial_query_set_data(device_association='', organization_ids=organization_ids)

    def get_initial_query_set_data(self, device_association='', **kwargs):
        device_list=list()
        devices= Device.objects.filter( organization__in= kwargs['organization_ids']).values(*self.columns+ \
                                                                        ['device_name', device_association])
        for device in devices:
            if device[device_association]:
                performance_data= PerformanceService.objects.raw('''select id, device_name, avg_value, sys_timestamp from \
                                  performance_performanceservice where id = (select MAX(id) from \
                                  performance_performanceservice where (device_name=%s and data_source=%s))''' \
                                                            ,[ device['device_name'], 'pl'])
                for data in performance_data:
                    device.update({'latency':data.avg_value, 'packet_loss':'pl', 'last_updated':
                                   str(datetime.datetime.fromtimestamp(float( data.sys_timestamp ))),
                                   'city':City.objects.get(id=device['city']).city_name,
                                   'state':State.objects.get(id=device['state']).state_name
                                 })
                    device_list.append(device)
        return device_list

    def prepare_results(self, qs):
        # if qs:
        #     qs = [ { key: val if val else "" for key, val in dct.items() } for dct in qs ]
        #     sanity_dicts_list = [OrderedDict({'dict_final_key':'full_name','dict_key1':'first_name', 'dict_key2':'last_name' }),
        #     OrderedDict({'dict_final_key':'manager_name', 'dict_key1':'parent__first_name', 'dict_key2':'parent__last_name'})]
        #     qs, qs_headers = Datatable_Generation( qs, sanity_dicts_list ).main()
        # #if the user role is Admin then the action column_values will appear on the datatable
        # if 'admin' in self.request.user.userprofile.role.values_list('role_name', flat=True):
        #     for dct in qs:
        #         dct.update(actions='<a href="/user/edit/{0}"><i class="fa fa-pencil text-dark"></i></a>\
        #                     <a href="#" onclick="Dajaxice.user_profile.user_soft_delete_form(get_soft_delete_form, {{\'value\': {0}}})"><i class="fa fa-trash-o text-danger"></i></a>'.format(dct.pop('id')))
        return qs

    def get_context_data(self, *args, **kwargs):
        request = self.request
        self.initialize(*args, **kwargs)

        qs = self.get_initial_queryset()

        # number of records before filtering
        total_records = len(qs)

        # qs = self.filter_queryset(qs)

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


    # def get(self, request, page_type = "no_page"):
    #
    #     # Customer live performance case
    #     if(page_type == "customer"):
    #
    #
    #         Device.objects.filter(id__in= SubStation.objects.all().values_list('device', flat=True), is_monitored_on_nms=1)
    #         return render(request, 'performance/customer_perf.html')
    #     # Network live performance case
    #     elif(page_type == "network"):
    #         return render(request, 'performance/network_perf.html')
    #     # Other live performance case
    #     else:
    #         return render(request, 'performance/other_perf.html')










class Get_Perfomance(View):

    def get(self, request, page_type = "no_page", device_id=0):
        page_data = {
                        'page_title' : page_type.capitalize(),
                        'device_id' : device_id,
                        'get_devices_url' : 'performance/get_inventory_devices/'+str(page_type),
                        'get_status_url' : 'performance/get_inventory_device_status/'+str(page_type)+'/device/'+str(device_id),
                        'get_services_url' : 'performance/get_inventory_service_data_sources/'+str(page_type)+'/device/'+str(device_id),
                        # 'get_service_data_url' : 'get_substation_services_data/'+str(device_id)+'/'
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

        if page_type =='customer':

            substation= SubStation.objects.get(id=device_id)
            substation_device= Device.objects.get(id= substation.device_id)
            sector= Circuit.objects.get(sub_station= substation.id).sector
            base_station= BaseStation.objects.get(id= Sector.objects.get(id=sector.id).base_station.id)
            result['data']['objects']['headers']= ['BS Name', 'SSName','Building Height', 'Tower Height',
                                                   'City', 'State', 'IP Address', 'MAC Address']
            result['data']['objects']['values']= [ base_station.name, substation.name,
                                                   str(substation.building_height), str(substation.tower_height),
                                                   substation.city, substation.state, substation_device.ip_address,
                                                   substation_device.mac_address ]

        elif page_type =='network':

            # base_station= BaseStation.objects.get(id=device_id)
            # sector_configured_on_device= Sector.objects.filter(base_station= base_station.id).values_list('sector_configured_on', flat=True)
            sector_configured_on_device= Device.objects.get(id=int(device_id))
            result['data']['objects']['headers']= ['BS Name', 'SSName','Building Height', 'Tower Height',
                                                   'City', 'State', 'IP Address', 'MAC Address']
            base_station_list= Sector.objects.filter(sector_configured_on= sector_configured_on_device.id).values_list('base_station', flat=True)
            if base_station_list:
                base_station=BaseStation.objects.get(id=base_station_list[0])
                result['data']['objects']['values']= [ base_station.name, str(base_station.building_height), str(base_station.tower_height),
                                                       base_station.city, base_station.state, sector_configured_on_device.ip_address,
                                                       sector_configured_on_device.mac_address ]

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
        if page_type =='customer':
            inventory_device= SubStation.objects.get(id= device_id)
            inventory_device_type_id= Device.objects.get(id= inventory_device.device_id).device_type

        elif page_type == 'network':
            #for basestation we need to fetch sector_configured_on device field from the device
            inventory_device_type_id= Device.objects.get(id=int(device_id)).device_type

        inventory_device_service_data_sources_ids= DeviceType.objects.get(id= inventory_device_type_id) \
            .service.values_list('service_data_sources', flat=True)
        inventory_device_service_data_sources_ids= filter(partial(is_not, None), inventory_device_service_data_sources_ids)
        if inventory_device_service_data_sources_ids:

            for inventory_device_service_data_sources_id in inventory_device_service_data_sources_ids:
                service_data_source=ServiceDataSource.objects.get(id= inventory_device_service_data_sources_id)
                result['data']['objects'].append({
                    'name':service_data_source.name,
                    'title':service_data_source.alias,
                    'url':'performance/service_data_source/'+ service_data_source.name +'/'+page_type+'/device/'+str(device_id),
                    'active':1
                })

            result['success']=1
            result['message']='Substation Devices Services Data Source Fetched Successfully.'
        return HttpResponse(json.dumps(result))


class Get_Service_Type_Performance_Data(View):

    def get(self, request, page_type, service_data_source_type, device_id):
        result={
        'success' : 0,
        'message' : 'Substation Service Not Fetched Successfully.',
        'data' : {
            'meta' : {},
            'objects' : {}
            }
        }
        if page_type =='customer':
            inventory_device_name= SubStation.objects.get(id= int(device_id)).name
        elif page_type == 'network':
            inventory_device_name=Device.objects.get(id=int(device_id)).device_name
        #raw query commented.
        # performance_data=PerformanceService.objects.raw('select id, max(id), avg_value, sys_timestamp from \
        #                 performance_performanceservice where data_source= {0} and device_name= {1} \
        #                 group by sys_timestamp order by id desc limit 6;'.format(service_data_source_type, substation_name))

        now=format(datetime.datetime.now(),'U')
        now_minus_30_min=format(datetime.datetime.now() + datetime.timedelta(minutes=-30), 'U')
        # performance_data=PerformanceService.objects.filter(device_name='bs_switch_dv_1', data_source='execution_time', sys_timestamp__gte='1404728700', sys_timestamp__lte='1404916800')
        performance_data=PerformanceService.objects.filter(device_name=inventory_device_name, \
                       data_source=service_data_source_type,sys_timestamp__gte=now_minus_30_min,sys_timestamp__lte=now )

        if performance_data:
            result['data']['objects']['type']='line'
            data_list=[]
            for data in performance_data:
                #data_list.append([data.sys_timestamp, data.avg_value ])
                data_list.append([data.sys_timestamp, float(data.avg_value) if data.avg_value else None])
                result['success']=1
                result['message']='Substation Service Fetched Successfully.'

            result['data']['objects']['chart_data']=[{'name': 'Latency', 'color':'#70AFC4', 'data': data_list } ]
        return HttpResponse(json.dumps(result), mimetype="application/json")


