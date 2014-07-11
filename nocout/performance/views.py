import json
import datetime
from django.db.models import Count
from django.http import HttpResponse
from django.shortcuts import render_to_response, render
from django.views.generic.base import View
from django.template import RequestContext

# Create your views here.
from device.models import Device, City, State, DeviceType

from inventory.models import SubStation, Circuit, Sector, BaseStation
from performance.models import PerformanceService
from service.models import Service, ServiceDataSource
from operator import is_not
from functools import partial
from django.utils.dateformat import format

class Get_Live_Performance(View):

    def get(self, request, page_type = "no_page"):

        # Customer live performance case
        if(page_type == "customer"):
            return render(request, 'performance/customer_perf.html')
        # Network live performance case
        elif(page_type == "network"):
            return render(request, 'performance/network_perf.html')
        # Other live performance case
        else:
            return render(request, 'performance/other_perf.html')

class Get_Perfomance(View):

    def get(self, request, page_type = "no_page", device_id=0):
        page_data = {
                        'page_title' : page_type.capitalize(),
                        'device_id' : device_id,
                        'get_devices_url' : 'get_inventory_devices/'+str(page_type)+'/',
                        'get_status_url' : 'get_inventory_device_status/'+str(page_type)+'/device/'+str(device_id)+'/',
                        'get_services_url' : 'get_inventory_service_data_sources'+str(page_type)+'/device/'+str(device_id)+'/',
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

        elif page_type == 'network':
            #for basestation we need to fetch sector_configured_on device field from the device
            inventory_device= Device.objects.get(id=int(device_id))

        inventory_device_type_id= Device.objects.get(id= inventory_device.id).device_type
        inventory_device_service_data_sources_ids= DeviceType.objects.get(id= inventory_device_type_id) \
            .service.values_list('service_data_sources', flat=True)
        inventory_device_service_data_sources_ids= filter(partial(is_not, None), inventory_device_service_data_sources_ids)
        if inventory_device_service_data_sources_ids:

            for inventory_device_service_data_sources_id in inventory_device_service_data_sources_ids:
                service_data_source=ServiceDataSource.objects.get(id= inventory_device_service_data_sources_id)
                result['data']['objects'].append({
                    'name':service_data_source.name,
                    'title':service_data_source.alias,
                    'url':'service_data_source/'+ service_data_source.name +'/'+page_type+'/device/'+str(device_id),
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
        performance_data=PerformanceService.objects.filter(device_name=inventory_device_name, data_source=service_data_source_type,
                         sys_timestamp__gte=now_minus_30_min,sys_timestamp__lte=now )

        if performance_data:
            result['data']['objects']['type']='line'
            data_list=[]
            for data in performance_data:
                data_list.append([data.sys_timestamp, data.avg_value ])
                result['success']=1
                result['message']='Substation Service Fetched Successfully.'

            result['data']['objects']['chart_data']=[{'name': 'Latency', 'color':'#70AFC4', 'data': data_list } ]
        return HttpResponse(json.dumps(result), mimetype="application/json")


