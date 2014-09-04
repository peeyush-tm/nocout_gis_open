import json, logging, datetime, xlwt, csv
from django.db.models import Count
from django.db.models.query import ValuesQuerySet
from django.http import HttpResponse
from django.shortcuts import render_to_response, render
from django.views.generic import ListView, View
from django.template import RequestContext
from django_datatables_view.base_datatable_view import BaseDatatableView
from device.models import Device, City, State, DeviceTechnology, DeviceType
from inventory.models import BaseStation, Sector, SubStation, Circuit, Backhaul
from performance.models import PerformanceNetwork, EventNetwork, EventService, NetworkStatus
from django.utils.dateformat import format
from django.db.models import Q
from nocout.settings import P2P
# going deep with sql cursor to fetch the db results. as the RAW query executes everythong it is recursively used
from django.db import connections

# for raw query optmisation we will use ceil
import math

# sort the list of dictionaries
# http://stackoverflow.com/questions/72899/how-do-i-sort-a-list-of-dictionaries-by-values-of-the-dictionary-in-python
from operator import itemgetter


logger = logging.getLogger(__name__)


def getNetworkAlert(request):
    """
    get request to render the network alert list

    :params request object:
    :return Http response object:
    """
    return render_to_response('alert_center/network_alerts_list.html', context_instance=RequestContext(request))


def getCustomerAlert(request, page_type="default_device_name"):
    """
    get request to render customer alert pages w.r.t page_type requested

    :params request object:
    :params page_type:
    :return Http response object:
    """
    if (page_type == "latency"):
        return render_to_response('alert_center/customer_latency_alerts_list.html',
                                  context_instance=RequestContext(request))
    else:
        return render_to_response('alert_center/customer_packet_alerts_list.html',
                                  context_instance=RequestContext(request))


def getCustomerAlertDetail(request):
    """
    get request to render customer detail list
    :params request object:
    :return Http Response Object::

    """
    customer_ptp_block_table_header = [
        {'mData': 'severity', 'sTitle': '', 'sWidth': '40px', 'bSortable': True},
        {'mData': 'device_name', 'sTitle': 'Device Name', 'sWidth': 'null', 'sClass': 'hidden-xs',
         'bSortable': True},
        {'mData': 'device_type', 'sTitle': 'Device type', 'sWidth': 'null', 'sClass': 'hidden-xs',
        'bSortable': True},
        {'mData': 'base_station', 'sTitle': 'Base Station', 'sWidth': 'null', 'sClass': 'hidden-xs',
         'bSortable': True},
        {'mData': 'circuit_id', 'sTitle': 'Circuit ID', 'sWidth': 'null', 'sClass': 'hidden-xs',
         'bSortable': True},
        {'mData': 'sector_id', 'sTitle': 'Sector ID', 'sWidth': 'null', 'sClass': 'hidden-xs',
         'bSortable': True},
        {'mData': 'device__city', 'sTitle': 'City', 'sWidth': 'null', 'sClass': 'hidden-xs',
         'bSortable': True},
        {'mData': 'device__state', 'sTitle': 'State', 'sWidth': 'null', 'sClass': 'hidden-xs',
         'bSortable': True},
        {'mData': 'data_source_name', 'sTitle': 'Data Source Name', 'sWidth': 'null', 'sClass': 'hidden-xs',
         'bSortable': True},
        {'mData': 'current_value', 'sTitle': 'Value', 'sWidth': 'null', 'sClass': 'hidden-xs',
         'bSortable': True},
        {'mData': 'sys_timestamp', 'sTitle': 'Timestamp', 'sWidth': 'null', 'bSortable': True},
        {'mData': 'action', 'sTitle': 'Action', 'sWidth': 'null', 'sClass': 'hidden-xs',
         'bSortable': False},
        ]

    context = {'customer_ptp_block_table_header': json.dumps(customer_ptp_block_table_header)}
    return render(request, 'alert_center/customer_alert_details_list.html', context)


class GetCustomerAlertDetail(BaseDatatableView):
    """
    Generic Class Based View for the Alert Center Customer Listing Tables.
    """
    model = EventNetwork
    columns = ['device_name', 'device_type', 'machine_name', 'site_name', 'ip_address', 'severity',
               'current_value', 'sys_timestamp', 'description']
    order_columns = ['device_name', 'device_type', 'machine_name', 'site_name', 'ip_address', 'severity',
                     'current_value', 'sys_timestamp', 'description']

    def filter_queryset(self, qs):
        """
        The filtering of the queryset with respect to the search keyword entered.

        :param qs:
        :return result_list:

        """
        sSearch = self.request.GET.get('sSearch', None)
        if sSearch:
            result_list = list()
            for dictionary in qs:
                for key in dictionary.keys():
                    if sSearch.lower() in str(dictionary[key]).lower():
                        result_list.append(dictionary)

            return result_list

        return qs

    def get_initial_queryset(self):
        """
        Preparing  Initial Queryset for the for rendering the data table.

        """
        if not self.model:
            raise NotImplementedError("Need to provide a model or implement get_initial_queryset!")

        logged_in_user = self.request.user.userprofile

        if logged_in_user.role.values_list('role_name', flat=True)[0] == 'admin':
            organizations = list(logged_in_user.organization.get_descendants(include_self=True))
        else:
            organizations = [logged_in_user.organization]

        organization_devices = list()
        device_tab_technology = self.request.GET.get('data_tab')
        device_technology_id = DeviceTechnology.objects.get(name=device_tab_technology).id
        # sector_configured_on_devices_ids=[]
        for organization in organizations:
            organization_devices += Device.objects.filter(is_added_to_nms=1, organization__id=organization.id,
                                                          device_technology=device_technology_id)

        # get the devices in an organisation which are added for monitoring
        organization_devices = [ {'device_name': device.device_name, 'machine_name': device.machine.name} \
                                 for device in organization_devices if device.substation_set.exists() or \
                                 device.sector_configured_on.exists() ]

        required_data_columns = ["id",
                                 "ip_address",
                                 "service_name",
                                 "device_name",
                                 "data_source",
                                 "severity",
                                 "current_value",
                                 "sys_timestamp",
                                 "description"
                                ]
        # Unique machine from the sector_configured_on_devices
        unique_machine_list = { device['machine_name']: True for device in organization_devices }.keys()

        machine_dict = dict()
        # Creating the machine as a key and device_name as a list for that machine.
        for machine in unique_machine_list:
            machine_dict[machine] = [ device['device_name'] for device in organization_devices if
                                      device['machine_name'] == machine ]

        #Fetching the data for the device w.r.t to their machine.
        device_list, performance_data, device_data = list(), list(), list()
        for machine, machine_device_list in machine_dict.items():
            data_sources_list = []
            device_data += self.collective_query_result(
                machine = machine,
                table_name = "performance_eventservice",
                devices = machine_device_list,
                data_sources = data_sources_list,
                columns = required_data_columns
            )

        if device_data:
            sorted_device_data = sorted(device_data, key=itemgetter('sys_timestamp'), reverse=True)
            return sorted_device_data

        return device_list


    def collective_query_result(self, machine, table_name, devices, data_sources, columns):

        performance_data = list()
        performance_data = raw_prepare_result(performance_data=performance_data,
                                              machine=machine,
                                              table_name=table_name,
                                              devices=devices,
                                              data_sources=data_sources,
                                              columns=columns
        )


        device_list = []
        for data in performance_data:
            device_object = Device.objects.get(device_name=data['device_name'])

            if device_object.substation_set.exists():
                
                device_circuit = ""
                device_basestation = ""
                has_circuit = False
                device_substation= SubStation.objects.get(id= device_object.substation_set.values_list('id', flat=True)[0])
                circuit_obj = Circuit.objects.filter(id= device_substation.circuit_set.values_list('id', flat=True))
                if len(circuit_obj):
                    device_circuit= circuit_obj[0]
                    device_basestation = device_circuit.sector.base_station.name
                    has_circuit = True

                if severity_level_check(list_to_check=[data['severity'], data['description']]):
                    device_events = {
                        'device_name': data["device_name"],
                        'device_type': DeviceType.objects.get(id=device_object.device_type).alias,
                        'severity': data['severity'],
                        # 'ip_address': data["ip_address"],
                        'base_station': device_basestation,
                        'circuit_id': device_circuit.circuit_id if has_circuit else "",
                        'sector_id': device_circuit.sector.sector_id if has_circuit else "",
                        'device__city': City.objects.get(id=device_object.city).city_name if device_object.city else 'N/A',
                        'device__state': State.objects.get(id=device_object.state).state_name if device_object.state else 'N/A',
                        'data_source_name': data["data_source"],
                        'current_value': data["current_value"],
                        # 'sys_time': datetime.datetime.fromtimestamp(float(data["sys_timestamp"])).strftime("%I:%M:%S %p"),
                        # 'sys_date': datetime.datetime.fromtimestamp(float(data["sys_timestamp"])).strftime("%d/%B/%Y"),
                        'sys_timestamp': datetime.datetime.fromtimestamp(float(data["sys_timestamp"])).strftime("%m/%d/%y (%b) %H:%M:%S (%I:%M %p)"),
                        'description': data['description']
                    }
                    device_list.append(device_events)

            elif device_object.sector_configured_on.exists():

                device_sector= Sector.objects.get(id= device_object.sector_configured_on.values_list('id', flat=True)[0])
                if severity_level_check(list_to_check=[data['severity'], data['description']]):
                    device_events = {
                        'device_name': data["device_name"],
                        'device_type': DeviceType.objects.get(id=device_object.device_type).alias,
                        'severity': data['severity'],
                        # 'ip_address': data["ip_address"],
                        'base_station': device_sector.base_station.name,
                        'circuit_id': device_sector.circuit_set.values_list('circuit_id', flat=True)[0],
                        'sector_id': device_sector.sector_id,
                        'device__city': City.objects.get(id=device_object.city).city_name if device_object.city else 'N/A',
                        'device__state': State.objects.get(id=device_object.state).state_name if device_object.state else 'N/A',
                        'data_source_name': data["data_source"],
                        'current_value': data["current_value"],
                        # 'sys_time': datetime.datetime.fromtimestamp(float(data["sys_timestamp"])).strftime("%I:%M:%S %p"),
                        # 'sys_date': datetime.datetime.fromtimestamp(float(data["sys_timestamp"])).strftime("%d/%B/%Y"),
                        'sys_timestamp': datetime.datetime.fromtimestamp(float(data["sys_timestamp"])).strftime("%m/%d/%y (%b) %H:%M:%S (%I:%M %p)"),
                        'description': data['description']
                    }
                    device_list.append(device_events)

        return device_list


    def prepare_results(self, qs):
        """
        Preparing the final result after fetching from the data base to render on the data table.

        :param qs:
        :return queryset
        """

        if qs:
            qs = [{key: val if val else "" for key, val in dct.items()} for dct in qs]

            service_tab_name = 'service'
            for dct in qs:
                device_object = Device.objects.get(device_name=dct['device_name'])
                device_id = device_object.id
                if device_object.substation_set.exists():

                    dct.update(action=''
                        '<a href="/alert_center/customer/device/{0}/service_tab/{1}/" title="Device Alerts">'
                        '<i class="fa fa-warning text-warning"></i>'
                        '</a>'
                        '<a href="/performance/customer_live/{0}/" title="Device Performance">'
                        '<i class="fa fa-bar-chart-o text-info"></i>'
                        '</a>'
                        '<a href="/device/{0}" title="Device Inventory">'
                        '<i class="fa fa-dropbox text-muted"></i>'
                        '</a>'.format(device_id, service_tab_name))

                elif device_object.sector_configured_on.exists():

                    dct.update(action=''
                       '<a href="/alert_center/customer/device/{0}/service_tab/{1}/" title="Device Alerts">'
                       '<i class="fa fa-warning text-warning"></i>'
                       '</a>'
                       '<a href="/performance/customer_live/{0}/" title="Device Performance">'
                       '<i class="fa fa-bar-chart-o text-info"></i>'
                       '</a>'
                       '<a href="/device/{0}" title="Device Inventory"><i class="fa fa-dropbox text-muted"></i></a>'
                       .format(device_id, service_tab_name))

        return common_prepare_results(qs)


    def get_context_data(self, *args, **kwargs):
        """
        The maine function call to fetch, search, ordering , prepare and display the data on the data table.

        """

        request = self.request
        self.initialize(*args, **kwargs)

        qs = self.get_initial_queryset()

        # number of records before filtering
        total_records = len(qs)

        qs = self.filter_queryset(qs)

        # number of records after filtering
        total_display_records = len(qs)

        # qs = self.ordering(qs)
        # qs = self.paging(qs)
        # if the qs is empty then JSON is unable to serialize the empty ValuesQuerySet.Therefore changing its type to list.
        if not qs and isinstance(qs, ValuesQuerySet):
            qs = list(qs)

        # prepare output data
        aaData = self.prepare_results(qs)
        ret = {
               'sEcho': int(request.REQUEST.get('sEcho', 0)),
               'iTotalRecords': total_records,
               'iTotalDisplayRecords': total_display_records,
               'aaData': aaData
              }
        return ret


def getNetworkAlertDetail(request):
    """
    get request to render network detail list
    :params request object:
    :return Http Response Object:
    """
    network_ptp_block_table_header = [
        {'mData': 'severity', 'sTitle': '', 'sWidth': '40px', 'bSortable': True},
        {'mData': 'device_name', 'sTitle': 'Device Name', 'sWidth': 'null', 'sClass': 'hidden-xs',
         'bSortable': True},
        {'mData': 'device_type', 'sTitle': 'Device Type', 'sWidth': 'null', 'sClass': 'hidden-xs',
        'bSortable': True},
        {'mData': 'base_station', 'sTitle': 'Base Station', 'sWidth': 'null', 'sClass': 'hidden-xs',
         'bSortable': True},
        {'mData': 'base_station__city', 'sTitle': 'City', 'sWidth': 'null', 'sClass': 'hidden-xs',
         'bSortable': True},
        {'mData': 'base_station__state', 'sTitle': 'State', 'sWidth': 'null', 'sClass': 'hidden-xs',
         'bSortable': True},
        {'mData': 'data_source_name', 'sTitle': 'Data Source Name', 'sWidth': 'null', 'sClass': 'hidden-xs',
         'bSortable': True},
        {'mData': 'current_value', 'sTitle': 'Value', 'sWidth': 'null', 'sClass': 'hidden-xs',
         'bSortable': True},
        {'mData': 'sys_timestamp', 'sTitle': 'Timestamp', 'sWidth': 'null', 'bSortable': True},
        {'mData': 'action', 'sTitle': 'Action', 'sWidth': 'null', 'bSortable': True},
        ]

    context = {'network_ptp_block_table_header': json.dumps(network_ptp_block_table_header)}
    return render(request, 'alert_center/network_alert_details_list.html', context)


class GetNetworkAlertDetail(BaseDatatableView):
    """
    Generic Class Based View for the Alert Center Network  Detail Listing Tables.

    """
    model = EventNetwork
    columns = ['device_name', 'device_type', 'machine_name', 'site_name', 'ip_address', 'severity',
               'current_value', 'sys_time', 'sys_date', 'description']
    order_columns = ['device_name', 'device_type', 'machine_name', 'site_name', 'ip_address', 'severity',
                     'current_value', 'sys_time', 'sys_date', 'description']

    def filter_queryset(self, qs):

        """
        The filtering of the queryset with respect to the search keyword entered.

        :param qs:
        :return result_list:
        """

        sSearch = self.request.GET.get('sSearch', None)
        if sSearch:
            result_list = list()
            for dictionary in qs:
                for key in dictionary.keys():
                    if sSearch.lower() in str(dictionary[key]).lower():
                        result_list.append(dictionary)
                        break
            return result_list
        return qs

    def get_initial_queryset(self):
        """
        Preparing  Initial Queryset for the for rendering the data table.

        """
        if not self.model:
            raise NotImplementedError("Need to provide a model or implement get_initial_queryset!")

        logged_in_user = self.request.user.userprofile

        if logged_in_user.role.values_list('role_name', flat=True)[0] == 'admin':
            organizations = list(logged_in_user.organization.get_descendants(include_self=True))
        else:
            organizations = [logged_in_user.organization]
        sector_configured_on_devices_ids = list()
        #here we would have to get the TAB wise content
        # we need to check the tabs
        # we need to check the data requested
        tab_id = None
        if self.request.GET.get("data_source"):
            tab_id = self.request.GET.get("data_source")
        else:
            return []

        ptp_backhaul_devices=[]
        sector_configured_on_devices = []

        if tab_id:
            if tab_id == "ptp_backhaul":
                #we need to search for devices with PTP backhaul type
                try:
                    #need to add device with Circuit Type as : Backhaul (@TODO: make this a dropdown menu item and must for the user)
                    #for technology = PTP and Circuit Type as Backhaul get the Device BH Configured On

                    circuit_ptp_bh = Circuit.objects.filter(circuit_type="Backhaul")
                    for cc in circuit_ptp_bh:
                        if cc.sector.base_station.backhaul.bh_configured_on.organization_id in organizations:
                            ptp_backhaul_devices.append({
                                "machine__name" : cc.sector.base_station.backhaul.bh_configured_on.machine.name,
                                "device_name" : cc.sector.base_station.backhaul.bh_configured_on.device_name
                            })
                        sector_configured_on_devices += ptp_backhaul_devices

                except:
                        pass
                        ##dont waste time on values if there are none


        else:
            return []

        # for organization in organizations:
        #     sector_configured_on_devices_ids += Sector.objects.filter(
        #         sector_configured_on__id__in=organization.device_set \
        #         .values_list('id', flat=True)).values_list('sector_configured_on', flat=True).annotate(
        #         dcount=Count('base_station'))
        #
        # sector_configured_on_devices = Device.objects.filter(~Q(device_technology = int(P2P.ID)),
        #                                                      is_added_to_nms=1, is_deleted=0,
        #                                                      id__in= sector_configured_on_devices_ids)\
        #                                                      .values('device_name', 'machine__name')

        device_list, performance_data, data_sources_list = list(), list(), list()

        required_data_columns = ["id",
                                 "ip_address",
                                 "service_name",
                                 "device_name",
                                 "data_source",
                                 "severity",
                                 "current_value",
                                 "sys_timestamp",
                                 "description"
                                ]
        # Unique machine from the sector_configured_on_devices
        unique_device_machine_list = {device['machine__name']: True for device in sector_configured_on_devices}.keys()
        machine_dict, device_data = dict(), list()
        # Creating the machine as a key and device_name as a list for that machine.
        for machine in unique_device_machine_list:
            machine_dict[machine] = [device['device_name']
                                     for device in sector_configured_on_devices
                                     if device['machine__name'] == machine]

        #Fetching the data for the device w.r.t to their machine.
        for machine, machine_device_list in machine_dict.items():

            # data_sources_list = ['rta', 'pl']
            #
            # device_data += self.collective_query_result(
            #     machine = machine,
            #     table_name = "performance_eventnetwork",
            #     devices = machine_device_list,
            #     data_sources = data_sources_list,
            #     columns = required_data_columns
            # )

            data_sources_list = []
            device_data += self.collective_query_result(
                machine = machine,
                table_name = "performance_eventservice",
                devices = machine_device_list,
                data_sources = data_sources_list,
                columns = required_data_columns,
                tab_source = tab_id
            )

        if device_data:
            sorted_device_data = sorted(device_data, key=itemgetter('sys_timestamp'), reverse=True)
            return sorted_device_data

        return device_list


    def collective_query_result(self, machine, table_name, devices, data_sources, columns, tab_source = "None"):
        if not tab_source:
            return []
        result_data = []
        performance_data = list() #self.model.objects.raw(query).using(alias=machine)
        performance_data = raw_prepare_result(performance_data=performance_data,
                                              machine=machine,
                                              table_name=table_name,
                                              devices=devices,
                                              data_sources=data_sources,
                                              columns=columns
        )

        for data in performance_data:

            city_name = ""
            state_name = ""
            base_station_name = ""

            device_object = Device.objects.get(device_name=data['device_name'])

            if tab_source == "ptp_backhaul":
                #ok now we have PTP backhaul device

                circuit_ptp_bh = Circuit.objects.filter(circuit_type="Backhaul")
                for cc in circuit_ptp_bh:
                    if cc.sector.base_station.backhaul.bh_configured_on.device_name == data["device_name"]:
                        base_station_obj = cc.sector.base_station
                        if base_station_obj:
                            base_station_name = base_station_obj.name
                            city_name = City.objects.get(id=base_station_obj.city).city_name if base_station_obj.city else 'N/A'
                            state_name = State.objects.get(id=base_station_obj.state).state_name if base_station_obj.state else "N/A"

                        if severity_level_check(list_to_check=[data['severity'], data['description']]):
                            ddata = {
                                'device_name': data['device_name'],
                                'device_type': DeviceType.objects.get(id=device_object.device_type).alias,
                                'severity': data['severity'],
                                'ip_address': data['ip_address'],
                                'base_station': base_station_name,
                                'base_station__city': city_name,
                                'base_station__state': state_name,
                                'data_source_name': data['data_source'],
                                'current_value': data['current_value'],
                                'sys_time': datetime.datetime.fromtimestamp(float(data['sys_timestamp'])).strftime("%I:%M:%S %p"),
                                'sys_date': datetime.datetime.fromtimestamp(float(data['sys_timestamp'])).strftime("%d/%B/%Y"),
                                'sys_timestamp': datetime.datetime.fromtimestamp(float(data['sys_timestamp'])).strftime("%m/%d/%y (%b) %H:%M:%S (%I:%M %p)"),
                                'description': data['description']
                            }
                            result_data.append(ddata)
            else:
                #we just have a case for PTP backhaul for now
                pass

        return result_data

    def prepare_results(self, qs):
        """
        Preparing the final result after fetching from the data base to render on the data table.

        :param qs:
        :return queryset.
        """

        if qs:
            qs = [{key: val if val else "" for key, val in dct.items()} for dct in qs]
            service_tab_name = 'service'
            for dct in qs:
                device_id = Device.objects.get(device_name=dct['device_name']).id
                dct.update(action='<a href="/alert_center/network/device/{0}/service_tab/{1}/" title="Device Alerts"><i class="fa fa-warning text-warning"></i></a>\
                                   <a href="/performance/network_live/{0}/" title="Device Performance"><i class="fa fa-bar-chart-o text-info"></i></a>\
                                   <a href="/device/{0}" title="Device Inventory"><i class="fa fa-dropbox text-muted"></i></a>'.format(device_id,
                                                                                                              service_tab_name))

        return common_prepare_results(qs)

    def get_context_data(self, *args, **kwargs):
        """
        The maine function call to fetch, search, prepare and display the data on the data table.

        """

        request = self.request
        self.initialize(*args, **kwargs)

        qs = self.get_initial_queryset()

        # number of records before filtering
        total_records = len(qs)

        qs = self.filter_queryset(qs)

        # number of records after filtering
        total_display_records = len(qs)

        # qs = self.ordering(qs)
        # qs = self.paging(qs)  # Removing pagination as of now to render all the data at once.
        # if the qs is empty then JSON is unable to serialize the empty ValuesQuerySet.Therefore changing its type to list.
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


# **************************************** Latency *********************************************
class AlertCenterNetworkListing(ListView):
    """
    Class Based View to render Alert Center Network Listing page with latency, packet drop
    down and service impact alert tabs.

    """
    model = EventNetwork
    template_name = 'alert_center/network_alerts_list.html'

    def get_context_data(self, **kwargs):
        """
        Preparing the Context Variable required in the template rendering.

        """
        context = super(AlertCenterNetworkListing, self).get_context_data(**kwargs)
        datatable_headers_latency = [

            {'mData': 'severity', 'sTitle': '', 'sWidth': '40px', 'bSortable': True},
            {'mData': 'device_name', 'sTitle': 'Device Name', 'sWidth': 'null', 'sClass': 'hidden-xs',
             'bSortable': True},
            {'mData': 'device_technology', 'sTitle': 'Tech', 'sWidth': 'null', 'sClass': 'hidden-xs',
             'bSortable': True},
            {'mData': 'device_type', 'sTitle': 'Type', 'sWidth': 'null', 'sClass': 'hidden-xs',
             'bSortable': True},
            # {'mData': 'ip_address', 'sTitle': 'IP Address', 'sWidth': 'null', 'sClass': 'hidden-xs',
            #  'bSortable': True},
            {'mData': 'base_station', 'sTitle': 'Base Station', 'sWidth': 'null', 'sClass': 'hidden-xs',
             'bSortable': True},
            {'mData': 'sector_id', 'sTitle': 'Sector ID', 'sWidth': 'null', 'sClass': 'hidden-xs',
             'bSortable': True},
            {'mData': 'circuit_id', 'sTitle': 'Circuit ID', 'sWidth': 'null', 'sClass': 'hidden-xs',
             'bSortable': True},
            {'mData': 'base_station__city', 'sTitle': 'City', 'sWidth': 'null', 'sClass': 'hidden-xs',
             'bSortable': True},
            {'mData': 'base_station__state', 'sTitle': 'State', 'sWidth': 'null', 'sClass': 'hidden-xs',
             'bSortable': True},
            {'mData': 'current_value', 'sTitle': 'Latency (ms)', 'sWidth': 'null', 'sClass': 'hidden-xs',
             'bSortable': True},
            {'mData': 'sys_timestamp', 'sTitle': 'Timestamp', 'sWidth': 'null', 'bSortable': True},
            {'mData': 'action', 'sTitle': 'Action', 'sWidth': 'null', 'bSortable': True},
            ]

        datatable_headers_packetdrop = [
            {'mData': 'severity', 'sTitle': '', 'sWidth': '40px', 'bSortable': True},
            {'mData': 'device_name', 'sTitle': 'Device Name', 'sWidth': 'null', 'sClass': 'hidden-xs',
             'bSortable': True},
            {'mData': 'device_technology', 'sTitle': 'Tech', 'sWidth': 'null', 'sClass': 'hidden-xs',
             'bSortable': True},
            {'mData': 'device_type', 'sTitle': 'Type', 'sWidth': 'null', 'sClass': 'hidden-xs',
             'bSortable': True},
            # {'mData': 'ip_address', 'sTitle': 'IP Address', 'sWidth': 'null', 'sClass': 'hidden-xs',
            #  'bSortable': True},
            {'mData': 'base_station', 'sTitle': 'Base Station', 'sWidth': 'null', 'sClass': 'hidden-xs',
             'bSortable': True},
            {'mData': 'sector_id', 'sTitle': 'Sector ID', 'sWidth': 'null', 'sClass': 'hidden-xs',
             'bSortable': True},
            {'mData': 'circuit_id', 'sTitle': 'Circuit ID', 'sWidth': 'null', 'sClass': 'hidden-xs',
             'bSortable': True},
            {'mData': 'base_station__city', 'sTitle': 'City', 'sWidth': 'null', 'sClass': 'hidden-xs',
             'bSortable': True},
            {'mData': 'base_station__state', 'sTitle': 'State', 'sWidth': 'null', 'sClass': 'hidden-xs',
             'bSortable': True},
            {'mData': 'current_value', 'sTitle': 'Packet Drop (%)', 'sWidth': 'null', 'sClass': 'hidden-xs',
             'bSortable': True},
            {'mData': 'sys_timestamp', 'sTitle': 'Timestamp', 'sWidth': 'null', 'bSortable': True},
            {'mData': 'action', 'sTitle': 'Action', 'sWidth': 'null', 'bSortable': True},
            ]
        datatable_headers_down = [
            {'mData': 'severity', 'sTitle': '', 'sWidth': '40px', 'bSortable': True},
            {'mData': 'device_name', 'sTitle': 'Device Name', 'sWidth': 'null', 'sClass': 'hidden-xs',
             'bSortable': True},
            {'mData': 'device_technology', 'sTitle': 'Tech', 'sWidth': 'null', 'sClass': 'hidden-xs',
             'bSortable': True},
            {'mData': 'device_type', 'sTitle': 'Type', 'sWidth': 'null', 'sClass': 'hidden-xs',
             'bSortable': True},
            # {'mData': 'ip_address', 'sTitle': 'IP Address', 'sWidth': 'null', 'sClass': 'hidden-xs',
            #  'bSortable': True},
            {'mData': 'base_station', 'sTitle': 'Base Station', 'sWidth': 'null', 'sClass': 'hidden-xs',
             'bSortable': True},
            {'mData': 'sector_id', 'sTitle': 'Sector ID', 'sWidth': 'null', 'sClass': 'hidden-xs',
             'bSortable': True},
            {'mData': 'circuit_id', 'sTitle': 'Circuit ID', 'sWidth': 'null', 'sClass': 'hidden-xs',
             'bSortable': True},
            {'mData': 'base_station__city', 'sTitle': 'City', 'sWidth': 'null', 'sClass': 'hidden-xs',
             'bSortable': True},
            {'mData': 'base_station__state', 'sTitle': 'State', 'sWidth': 'null', 'sClass': 'hidden-xs',
             'bSortable': True},
            {'mData': 'current_value', 'sTitle': 'Packet Drop (%)', 'sWidth': 'null', 'sClass': 'hidden-xs',
             'bSortable': True},
            {'mData': 'sys_timestamp', 'sTitle': 'Timestamp', 'sWidth': 'null', 'bSortable': True},
            {'mData': 'action', 'sTitle': 'Action', 'sWidth': 'null', 'bSortable': True},
            ]
        datatable_headers_servicealerts = [
            {'mData': 'severity', 'sTitle': '', 'sWidth': '40px', 'bSortable': True},
            {'mData': 'device_name', 'sTitle': 'Device Name', 'sWidth': 'null', 'sClass': 'hidden-xs',
             'bSortable': True},
            {'mData': 'device_technology', 'sTitle': 'Tech', 'sWidth': 'null', 'sClass': 'hidden-xs',
             'bSortable': True},
            {'mData': 'device_type', 'sTitle': 'Type', 'sWidth': 'null', 'sClass': 'hidden-xs',
             'bSortable': True},
            # {'mData': 'ip_address', 'sTitle': 'IP Address', 'sWidth': 'null', 'sClass': 'hidden-xs',
            #  'bSortable': True},
            {'mData': 'base_station', 'sTitle': 'Base Station', 'sWidth': 'null', 'sClass': 'hidden-xs',
             'bSortable': True},
            {'mData': 'sector_id', 'sTitle': 'Sector ID', 'sWidth': 'null', 'sClass': 'hidden-xs',
             'bSortable': True},
            {'mData': 'circuit_id', 'sTitle': 'Circuit ID', 'sWidth': 'null', 'sClass': 'hidden-xs',
             'bSortable': True},
            {'mData': 'base_station__city', 'sTitle': 'City', 'sWidth': 'null', 'sClass': 'hidden-xs',
             'bSortable': True},
            {'mData': 'base_station__state', 'sTitle': 'State', 'sWidth': 'null', 'sClass': 'hidden-xs',
             'bSortable': True},
            {'mData': 'data_source_name', 'sTitle': 'Data Source Name', 'sWidth': 'null', 'sClass': 'hidden-xs',
             'bSortable': True},
            {'mData': 'sys_timestamp', 'sTitle': 'Timestamp', 'sWidth': 'null', 'bSortable': True},
            {'mData': 'current_value', 'sTitle': 'Value', 'sWidth': 'null', 'sClass': 'hidden-xs',
             'bSortable': True},
            {'mData': 'action', 'sTitle': 'Action', 'sWidth': 'null', 'bSortable': True},
            ]
        context['datatable_headers_servicealerts'] = json.dumps(datatable_headers_servicealerts)
        context['datatable_headers_down'] = json.dumps(datatable_headers_down)
        context['datatable_headers_packetdrop'] = json.dumps(datatable_headers_packetdrop)
        context['datatable_headers_latency'] = json.dumps(datatable_headers_latency)
        return context


class AlertCenterNetworkListingTable(BaseDatatableView):
    """
    Generic Class Based View for the Alert Center Network Listing Tables.

    """
    model = EventNetwork
    columns = ['device_name', "device_technology", "device_type" ,'machine_name', 'site_name', 'ip_address', 'severity',
               'current_value', "device_technology", "device_type", 'sys_timestamp', 'description']
    order_columns = ['device_name',  "device_technology", "device_type", 'machine_name', 'site_name', 'ip_address', 'severity',
                     'current_value', 'sys_timestamp', 'description']

    def filter_queryset(self, qs):

        """
        The filtering of the queryset with respect to the search keyword entered.

        :param qs:
        :return result_list:
        """

        sSearch = self.request.GET.get('sSearch', None)
        if sSearch:
            result_list = list()
            for dictionary in qs:
                for key in dictionary.keys():
                    if sSearch.lower() in str(dictionary[key]).lower():
                        result_list.append(dictionary)
                        break
            return result_list
        return qs

    def get_initial_queryset(self):
        """
        Preparing  Initial Queryset for the for rendering the data table.

        """
        if not self.model:
            raise NotImplementedError("Need to provide a model or implement get_initial_queryset!")

        logged_in_user = self.request.user.userprofile

        if logged_in_user.role.values_list('role_name', flat=True)[0] == 'admin':
            organizations_ids = list(logged_in_user.organization.get_descendants(include_self=True).values_list('id', flat=True))
        else:
            organizations_ids = [logged_in_user.organization.id]

        sector_configured_on_devices = Device.objects.filter(~Q(device_technology = int(P2P.ID)), is_added_to_nms=1,
                                                             is_deleted=0, sector_configured_on__isnull=False,
                                                             organization__in= organizations_ids)\
                                                             .values('device_name', 'machine__name')



        sector_configured_on_devices = list(sector_configured_on_devices)
        ptp_backhaul_devices = []

        try:
            #need to add device with Circuit Type as : Backhaul (@TODO: make this a dropdown menu item and must for the user)
            #for technology = PTP and Circuit Type as Backhaul get the Device BH Configured On

            circuit_ptp_bh = Circuit.objects.filter(circuit_type="Backhaul")
            for cc in circuit_ptp_bh:
                ptp_backhaul_devices.append({
                    "machine__name" : cc.sector.base_station.backhaul.bh_configured_on.machine.name,
                    "device_name" : cc.sector.base_station.backhaul.bh_configured_on.device_name
                })
            sector_configured_on_devices += ptp_backhaul_devices
        except Exception as e:
            pass
            ##dont waste time on values if there are none



        device_list, performance_data, data_sources_list = list(), list(), list()
        extra_query_condition = None

        search_table = "performance_eventnetwork"

        if 'latency' in self.request.path_info:
            data_sources_list.append('rta')
            extra_query_condition = "AND (`{0}`.`current_value` > 0 ) "
        elif 'packetdrop' in self.request.path_info:
            data_sources_list.append('pl')
            extra_query_condition = "AND (`{0}`.`current_value` BETWEEN 1 AND 99 ) "
        elif 'down' in self.request.path_info:
            data_sources_list.append('pl')
            extra_query_condition = "AND (`{0}`.`current_value` = 100 ) "
        elif 'service' in self.request.path_info:
            search_table = "performance_eventservice"

        required_data_columns = ["id",
                                 "ip_address",
                                 "service_name",
                                 "device_name",
                                 "data_source",
                                 "severity",
                                 "current_value",
                                 "sys_timestamp",
                                 "description"
        ]
        # Unique machine from the sector_configured_on_devices
        unique_device_machine_list = {device['machine__name']: True for device in sector_configured_on_devices}.keys()
        machine_dict, device_data = dict(), list()
        # Creating the machine as a key and device_name as a list for that machine.
        for machine in unique_device_machine_list:
            machine_dict[machine] = [device['device_name'] for device in sector_configured_on_devices if
                                     device['machine__name'] == machine]
        #Fetching the data for the device w.r.t to their machine.
        for machine, machine_device_list in machine_dict.items():

            performance_data = raw_prepare_result(performance_data=performance_data,
                                                  machine=machine,
                                                  table_name=search_table,
                                                  devices=machine_device_list,
                                                  data_sources=data_sources_list,
                                                  columns=required_data_columns,
                                                  condition=extra_query_condition if extra_query_condition else None
            )


            for data in performance_data:

                circuit_id = "N/A"
                sector_id = 'N/A'
                sector = Sector.objects.filter(sector_configured_on__id=
                                               Device.objects.get(device_name= data['device_name']).id)
                device_object = Device.objects.get(device_name= data['device_name'])
                #now comes special case; wherein device is either backhaul or sector configured on
                #we need to make a check to identify whats what

                backhaul = Backhaul.objects.filter(bh_configured_on__device_name=data['device_name'])

                if len(sector):

                    #add sector info
                    sector_id = sector[0].sector_id
                    #add circuit info
                    circuit = Circuit.objects.filter(sector=sector[0].id)
                    if len(circuit):
                        circuit_id = circuit[0].circuit_id

                    device_base_station = sector[0].base_station
                    #only display warning or critical devices
                    if severity_level_check(list_to_check=[data['severity'], data['description']]):
                        ddata = {
                            'device_name': data['device_name'],
                            'device_technology': DeviceTechnology.objects.get(id=device_object.device_technology).alias,
                            'device_type': DeviceType.objects.get(id=device_object.device_type).alias,
                            'severity': data['severity'],
                            'ip_address': data['ip_address'],
                            'circuit_id': circuit_id,
                            'sector_id': sector_id,
                            'base_station': device_base_station.name,
                            'base_station__city': City.objects.get(id=device_base_station.city).city_name if device_base_station.city else 'N/A',
                            'base_station__state': State.objects.get(id=device_base_station.state).state_name if device_base_station.state else "N/A",
                            'current_value': data['current_value'],
                            'sys_timestamp': datetime.datetime.fromtimestamp(
                                float(data['sys_timestamp'])).strftime("%m/%d/%y (%b) %H:%M:%S (%I:%M %p)"),
                            'description': data['description']
                        }
                        #If service tab is requested then add an another key:data_source_name to render in the data table.
                        if 'service' in self.request.path_info:
                            ddata.update({'data_source_name': data['data_source']})
                        device_data.append(ddata)

                elif len(backhaul):
                    #no sector circuit in that case : Just an assumption. Needs to be checked with the client
                    #one backhaul might be serving many a base staions # TODO resolve this
                    circuit_id = ""
                    sector_id = ""
                    device_base_station = ""
                    city = ""
                    state = ""
                    device_base_station_obj = backhaul.basestation_set.filter()
                    if len(device_base_station_obj):
                        device_base_station = device_base_station_obj[0]
                        city = City.objects.get(id=device_base_station.city).city_name if device_base_station.city else 'N/A'
                        state = State.objects.get(id=device_base_station.state).state_name if device_base_station.state else "N/A"
                    #we have got ourselves a backhaul device that too of a PTP
                    # if not PTP then exception and let it pass
                    if severity_level_check(list_to_check=[data['severity'], data['description']]):
                        ddata = {
                            'device_name': data['device_name'],
                            'device_technology': DeviceTechnology.objects.get(id=device_object.device_technology).alias,
                            'device_type': DeviceType.objects.get(id=device_object.device_type).alias,
                            'severity': data['severity'],
                            'ip_address': data['ip_address'],
                            'circuit_id': circuit_id,
                            'sector_id': sector_id,
                            'base_station': device_base_station.name,
                            'base_station__city': city,
                            'base_station__state': state,
                            'current_value': data['current_value'],
                            'sys_timestamp': datetime.datetime.fromtimestamp(
                                float(data['sys_timestamp'])).strftime("%m/%d/%y (%b) %H:%M:%S (%I:%M %p)"),
                            'description': data['description']
                        }
                        #If service tab is requested then add an another key:data_source_name to render in the data table.
                        if 'service' in self.request.path_info:
                            ddata.update({'data_source_name': data['data_source']})
                        device_data.append(ddata)
                else:
                    #go on for loop. we are not concerned
                    pass
        if device_data:
            sorted_device_data = sorted(device_data, key=itemgetter('sys_timestamp'), reverse=True)
            return sorted_device_data

        return device_list


    def prepare_results(self, qs):
        """
        Preparing the final result after fetching from the data base to render on the data table.

        :param qs:
        :return queryset.
        """

        if qs:
            qs = [{key: val if val else "" for key, val in dct.items()} for dct in qs]
            service_tab_name = None
            # figure out which tab call is made.
            if 'latency' in self.request.path_info:
                service_tab_name = 'latency'
            elif 'packetdrop' in self.request.path_info:
                service_tab_name = 'packetdrop'
            elif 'down' in self.request.path_info:
                service_tab_name = 'down'
            elif 'service' in self.request.path_info:
                service_tab_name = 'service'

            for dct in qs:
                device_id = Device.objects.get(device_name=dct['device_name']).id
                dct.update(action='<a href="/alert_center/network/device/{0}/service_tab/{1}/" title="Device Alerts"><i class="fa fa-warning text-warning"></i></a>\
                                   <a href="/performance/network_live/{0}/" title="Device Performance"><i class="fa fa-bar-chart-o text-info"></i></a>\
                                   <a href="/device/{0}" title="Device Inventory"><i class="fa fa-dropbox text-muted"></i></a>'.format(device_id,
                                                                                                              service_tab_name))

        return common_prepare_results(qs)

    def get_context_data(self, *args, **kwargs):
        """
        The maine function call to fetch, search, prepare and display the data on the data table.

        """

        request = self.request
        self.initialize(*args, **kwargs)

        qs = self.get_initial_queryset()

        # number of records before filtering
        total_records = len(qs)

        qs = self.filter_queryset(qs)

        # number of records after filtering
        total_display_records = len(qs)

        # qs = self.ordering(qs)
        # qs = self.paging(qs) #Removing pagination as of now to render all the data at once.
        # if the qs is empty then JSON is unable to serialize the empty ValuesQuerySet.Therefore changing its type to list.
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


class CustomerAlertList(ListView):
    """
    Class Based View to render Alert Center Customer Listing page.

    """
    model = EventNetwork
    template_name = 'alert_center/customer_alerts_list.html'

    def get_context_data(self, **kwargs):
        """
        Preparing the Context Variable required in the template rendering.

        """

        context = super(CustomerAlertList, self).get_context_data(**kwargs)
        data_source=self.kwargs.get('data_source','')
        datatable_headers = [
            {'mData': 'severity', 'sTitle': '', 'sWidth': '40px', 'bSortable': True},
            {'mData': 'device_name', 'sTitle': 'Device Name', 'sWidth': 'null', 'sClass': 'hidden-xs',
             'bSortable': True},
            # {'mData': 'device_technology', 'sTitle': 'Tech', 'sWidth': 'null', 'sClass': 'hidden-xs',
            #  'bSortable': True},
            {'mData': 'device_type', 'sTitle': 'Type', 'sWidth': 'null', 'sClass': 'hidden-xs',
             'bSortable': True},
            # {'mData': 'ip_address', 'sTitle': 'IP', 'sWidth': 'null', 'sClass': 'hidden-xs', 'bSortable': True},
            # {'mData': 'sub_station', 'sTitle': 'Sub Station', 'sWidth': 'null', 'sClass': 'hidden-xs',
            #  'bSortable': True},
            {'mData': 'city', 'sTitle': 'City', 'sWidth': 'null', 'sClass': 'hidden-xs',
             'bSortable': True},
            {'mData': 'state', 'sTitle': 'State', 'sWidth': 'null', 'sClass': 'hidden-xs',
             'bSortable': True},
            {'mData': 'base_station', 'sTitle': 'Base Station', 'sWidth': 'null', 'sClass': 'hidden-xs',
             'bSortable': True},
            {'mData': 'circuit_id', 'sTitle': 'Circuit ID', 'sWidth': 'null', 'sClass': 'hidden-xs',
             'bSortable': True},
            {'mData': 'sector_id', 'sTitle': 'Sector ID', 'sWidth': 'null', 'sClass': 'hidden-xs',
             'bSortable': True},
            {'mData': 'current_value', 'sTitle': 'Packet Drop %', 'sWidth': 'null', 'sClass': 'hidden-xs',
             'bSortable': True }
             if data_source.lower() in ['down','packet_drop'] else
            {'mData': 'current_value', 'sTitle': 'Latency Average(ms)', 'sWidth': 'null', 'sClass': 'hidden-xs',
             'bSortable': True },
            {'mData': 'sys_timestamp', 'sTitle': 'Timestamp', 'sWidth': 'null', 'bSortable': True},
            {'mData': 'action', 'sTitle': 'Action', 'sWidth': 'null', 'bSortable': True},
            ]

        if data_source.lower() =='latency' : datatable_headers.insert(len(datatable_headers)-2,
        {'mData': 'max_value', 'sTitle': 'Max Latency(ms)', 'sWidth': 'null', 'sClass': 'hidden-xs',
        'bSortable': True })

        context['datatable_headers'] = json.dumps(datatable_headers)
        context['data_source'] = " ".join(self.kwargs['data_source'].split('_')).title()
        return context


class CustomerAlertListingTable(BaseDatatableView):
    """
    Generic Class Based View for the Alert Center Customer Listing Tables.
    """
    model = EventNetwork
    columns = ['device_name', 'device_type', 'machine_name', 'site_name', 'ip_address', 'severity',
               'current_value', 'sys_timestamp', 'description']
    order_columns = ['device_name', 'device_type', 'machine_name', 'site_name', 'ip_address', 'severity',
                     'current_value', 'sys_timestamp', 'description']

    def filter_queryset(self, qs):
        """
        The filtering of the queryset with respect to the search keyword entered.

        :param qs:
        :return result_list:

        """
        sSearch = self.request.GET.get('sSearch', None)
        if sSearch:
            result_list = list()
            for dictionary in qs:
                for key in dictionary.keys():
                    if sSearch.lower() in str(dictionary[key]).lower():
                        result_list.append(dictionary)

            return result_list

        return qs

    def get_initial_queryset(self):
        """
        Preparing  Initial Queryset for the for rendering the data table.

        """
        if not self.model:
            raise NotImplementedError("Need to provide a model or implement get_initial_queryset!")

        logged_in_user = self.request.user.userprofile

        if logged_in_user.role.values_list('role_name', flat=True)[0] == 'admin':
            organizations_ids = list(logged_in_user.organization.get_descendants(include_self=True).values_list('id', flat=True))
        else:
            organizations_ids = [logged_in_user.organization]

        device_tab_name = self.request.GET.get('data_tab')
        device_technology_id = DeviceTechnology.objects.get(name= device_tab_name).id
        #IF Device Technology is P2P then fetch sector_configured_on as well as substation foreign keys relation present device
        if device_technology_id ==int(P2P.ID):
            devices = Device.objects.filter(Q(sector_configured_on__isnull=False) | Q(substation__isnull=False),
                                            is_added_to_nms=1, organization__in= organizations_ids,
                                                          device_technology= device_technology_id,
                                                         )
        #else Fecth all the devices which has substation as a foreign key relation present with the device.
        else:
            devices = Device.objects.filter(substation__isnull=False,
                                            is_added_to_nms=1, organization__in= organizations_ids,
                                            device_technology= device_technology_id)

        organization_substations_devices = [ {'device_name': device.device_name, 'machine_name': device.machine.name} \
                                             for device in devices ]

        data_sources_list = list()

        extra_query_condition = "AND (`{0}`.`current_value` > 0 ) "

        if self.request.GET['data_source'] == 'latency':
            data_sources_list = ['rta']
        elif self.request.GET['data_source'] == 'packet_drop':
            data_sources_list = ['pl']
            extra_query_condition = "AND (`{0}`.`current_value` BETWEEN 1 AND 99 ) "
        elif self.request.GET['data_source'] == 'down':
            data_sources_list = ['pl']
            extra_query_condition = "AND (`{0}`.`current_value` = 100 ) "

        required_data_columns = ["id",
                                 "data_source",
                                 "device_name",
                                 "severity",
                                 "current_value",
                                 "max_value",
                                 "sys_timestamp",
                                 "description"]

        # Unique machine from the sector_configured_on_devices
        unique_device_machine_list = {device['machine_name']: True for device in
                                      organization_substations_devices}.keys()
        machine_dict = dict()
        # Creating the machine as a key and device_name as a list for that machine.
        for machine in unique_device_machine_list:
            machine_dict[machine] = [device['device_name'] for device in organization_substations_devices if
                                     device['machine_name'] == machine]
        #Fetching the data for the device w.r.t to their machine.
        device_list, performance_data = list(), list()

        for machine, machine_device_list in machine_dict.items():

            performance_data = raw_prepare_result(performance_data=performance_data,
                                                  machine=machine,
                                                  table_name='performance_eventnetwork',
                                                  devices=machine_device_list,
                                                  data_sources=data_sources_list,
                                                  columns=required_data_columns,
                                                  condition= extra_query_condition )

            for data in performance_data:
                # for device in machine_device_list:
                device = data['device_name']
                device_object = Device.objects.get(device_name=device)


                if device_object.substation_set.exists():
                    device_substation = SubStation.objects.get(id= device_object.substation_set.values_list('id', flat=True)[0])

                    if device_substation.circuit_set.exists():
                        circuit_object = Circuit.objects.get(sub_station__id= device_substation.id)
                        circuit_id = circuit_object.circuit_id
                        sector_id = circuit_object.sector.sector_id
                        device_substation_base_station = circuit_object.sector.base_station
                        device_substation_base_station_name = device_substation_base_station.name
                        city = City.objects.get(id=device_substation_base_station.city).city_name
                        state= State.objects.get(id=device_substation_base_station.state).state_name
                    else:
                        device_substation_base_station_name = 'N/A'
                        city = "N/A"
                        state = "N/A"
                        sector_id = "N/A"
                        circuit_id = "N/A"

                    #only display warning or critical devices
                    if data['severity'] in ['DOWN', 'CRITICAL', 'WARNING', 'UNKNOWN'] or \
                                    'WARN' in data['description'] or \
                                    'CRIT' in data['description']:
                        device_object = Device.objects.get(device_name=device)
                        device_events = {
                            'device_name': device,
                            'severity': data['severity'],
                            # 'device_technology': DeviceTechnology.objects.get(id=device_object.device_technology).alias,
                            'device_type': DeviceType.objects.get(id=device_object.device_type).alias,
                            # 'ip_address': device_object.ip_address,
                            # 'sub_station': device_substation.name,
                            'city': city,
                            'state': state,
                            'base_station': device_substation_base_station_name,
                            'circuit_id': circuit_id,
                            'sector_id': sector_id,
                            'current_value': data['current_value'],
                            'max_value':data['max_value'],
                            'sys_time': datetime.datetime.fromtimestamp(
                                float(data['sys_timestamp'])).strftime("%I:%M:%S %p"),
                            'sys_date': datetime.datetime.fromtimestamp(
                                float(data['sys_timestamp'])).strftime("%d/%B/%Y"),
                            'sys_timestamp': datetime.datetime.fromtimestamp(
                                float(data['sys_timestamp'])).strftime("%m/%d/%y (%b) %H:%M:%S (%I:%M %p)"),
                            'description': data['description']
                        }
                        device_list.append(device_events)

                if device_object.sector_configured_on.exists():

                    circuit_id = "N/A"
                    sector_id = 'N/A'

                    sectors = Sector.objects.filter(sector_configured_on=device_object.id).values("id", "sector_id", "base_station")
                    sector_id_list = [x["id"] for x in sectors]
                    sector_id = ", ".join(map( str, [ x["sector_id"] for x in sectors ] ))

                    circuits = Circuit.objects.filter(sector__in= sector_id_list).values("circuit_id")
                    if len(circuits):
                        circuits_id_list = [x["circuit_id"] for x in circuits]
                        circuit_id = ",".join(map(lambda x: str(x), circuits_id_list ))

                    device_base_station = BaseStation.objects.get(id= sectors[0]["base_station"] )
                    #only display warning or critical devices
                    if severity_level_check(list_to_check=[data['severity'], data['description']]):
                        ddata = {
                            'device_name': data['device_name'],
                            # 'device_technology': DeviceTechnology.objects.get(id=device_object.device_technology).alias,
                            'device_type': DeviceType.objects.get(id= device_object.device_type).alias,
                            'severity': data['severity'],
                            'circuit_id': circuit_id,
                            'sector_id': sector_id,
                            'base_station': device_base_station.name,
                            'city': City.objects.get(id=device_base_station.city).city_name if device_base_station.city else 'N/A',
                            'state': State.objects.get(id=device_base_station.state).state_name if device_base_station.state else "N/A",
                            'current_value': data['current_value'],
                            'max_value':data['max_value'],
                            'sys_timestamp': datetime.datetime.fromtimestamp(
                                float(data['sys_timestamp'])).strftime("%m/%d/%y (%b) %H:%M:%S (%I:%M %p)"),
                            'description': data['description']
                        }
                        #If service tab is requested then add an another key:data_source_name to render in the data table.
                        # if 'service' in self.request.path_info:
                        #     ddata.update({'data_source_name': data['data_source']})
                        device_list.append(ddata)

            sorted_device_list = sorted(device_list, key=itemgetter('sys_timestamp'), reverse=True)
            return sorted_device_list

        return device_list

    def prepare_results(self, qs):
        """
        Preparing the final result after fetching from the data base to render on the data table.

        :param qs:
        :return queryset
        """

        if qs:
            qs = [{key: val if val else "" for key, val in dct.items()} for dct in qs]
            data_unit = "%"
            service_tab = 'down'
            # figure out which tab call is made.
            data_source = self.request.GET.get('data_source', '')
            if 'latency' == data_source:
                service_tab = 'latency'
                data_unit = "ms"
            elif 'packet_drop' == data_source:
                service_tab = 'packet_drop'

            for dct in qs:
                device = Device.objects.get(device_name= dct['device_name'])
                dct.update(current_value = dct["current_value"] + " " + data_unit)
                dct.update(action='<a href="/alert_center/customer/device/{0}/service_tab/{1}/" title="Device Alerts"><i class="fa fa-warning text-warning"></i></a>\
                                       <a href="/performance/customer_live/{0}/" title="Device Performance"><i class="fa fa-bar-chart-o text-info"></i></a>\
                                       <a href="/device/{0}" title="Device Inventory"><i class="fa fa-dropbox text-muted"></i></a>'.
                               format(device.id, service_tab ))

            return common_prepare_results(qs)

        return []


    def get_context_data(self, *args, **kwargs):
        """
        The maine function call to fetch, search, ordering , prepare and display the data on the data table.

        """

        request = self.request
        self.initialize(*args, **kwargs)

        qs = self.get_initial_queryset()

        # number of records before filtering
        total_records = len(qs)

        qs = self.filter_queryset(qs)

        # number of records after filtering
        total_display_records = len(qs)

        # qs = self.ordering(qs)
        # qs = self.paging(qs)
        # if the qs is empty then JSON is unable to serialize the empty ValuesQuerySet.Therefore changing its type to list.
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


class SingleDeviceAlertDetails(View):
    """
    Generic Class for Network and Customer to render the details page for a single device.
    """

    def get(self, request, page_type, device_id, service_name):

        logged_in_user, devices_result = request.user.userprofile, list()

        if 'admin' in logged_in_user.role.values_list('role_name', flat=True):
            organizations_ids = list(logged_in_user.organization.get_descendants(include_self=True).values_list('id', flat=True))
        else:
            organizations_ids = [logged_in_user.organization.id]

        devices_result += self.get_result(page_type, organizations_ids)

        start_date= self.request.GET.get('start_date','')
        end_date= self.request.GET.get('end_date','')
        isSet = False

        if len(start_date) and len(end_date):
            start_date_object= datetime.datetime.strptime( start_date +" 00:00:00", "%d-%m-%Y %H:%M:%S" )
            end_date_object= datetime.datetime.strptime( end_date + " 23:59:59", "%d-%m-%Y %H:%M:%S" )
            start_date= format( start_date_object, 'U')
            end_date= format( end_date_object, 'U')
            isSet = True
            if start_date == end_date:
                # Converting the end date to the highest time in a day.
                end_date_object = datetime.datetime.strptime(end_date + " 23:59:59", "%d-%m-%Y %H:%M:%S")
        else:
            # The end date is the end limit we need to make query till.
            end_date_object = datetime.datetime.now()
            # The start date is the last monday of the week we need to calculate from.
            start_date_object = end_date_object - datetime.timedelta(days=end_date_object.weekday())
            # Replacing the time, to start with the 00:00:00 of the last monday obtained.
            start_date_object = start_date_object.replace(hour=00, minute=00, second=00, microsecond=00)
            # Converting the date to epoch time or Unix Timestamp
            end_date = format(end_date_object, 'U')
            start_date = format(start_date_object, 'U')
            isSet = True


        device_obj = Device.objects.get(id= device_id)
        device_name = device_obj.device_name
        machine_name = device_obj.machine.name

        data_list = None
        required_columns = ["device_name", "ip_address", "service_name", "data_source",
                            "severity", "current_value", "sys_timestamp", "description"]
        if service_name == 'latency':
            data_list = EventNetwork.objects. \
                filter(device_name=device_name,
                       data_source='rta',
                       sys_timestamp__gte=start_date,
                       sys_timestamp__lte=end_date). \
                order_by("-sys_timestamp"). \
                values(*required_columns).using(alias=machine_name)

        elif service_name == 'packetdrop' or service_name == 'packet_drop':
            data_list = EventNetwork.objects. \
                filter(device_name=device_name,
                       data_source='pl',
                       sys_timestamp__gte=start_date,
                       sys_timestamp__lte=end_date). \
                order_by("-sys_timestamp"). \
                values(*required_columns).using(alias=machine_name)

        elif service_name == 'down':
            data_list = EventNetwork.objects. \
                filter(device_name=device_name,
                       data_source='pl',
                       current_value=100,
                       severity='DOWN',
                       sys_timestamp__gte=start_date,
                       sys_timestamp__lte=end_date). \
                order_by("-sys_timestamp"). \
                values(*required_columns).using(alias=machine_name)

        elif service_name == 'service':
            data_list = EventService.objects. \
                filter(device_name=device_name,
                       sys_timestamp__gte=start_date,
                       sys_timestamp__lte=end_date). \
                order_by("-sys_timestamp"). \
                values(*required_columns).using(alias=machine_name)

        required_columns = [
            "device_name",
            "ip_address",
            "service_name",
            "data_source",
            "severity",
            "current_value",
            "alert_date",
            "alert_time",
            "description"
        ]
        for data in data_list:
            data["alert_date"] = datetime.datetime. \
                fromtimestamp(float(data["sys_timestamp"])). \
                strftime("%d/%B/%Y")
            data["alert_time"] = datetime.datetime. \
                fromtimestamp(float(data["sys_timestamp"])). \
                strftime("%I:%M %p")
            del (data["sys_timestamp"])

        download_excel = self.request.GET.get('download_excel', '')
        download_csv = self.request.GET.get('download_csv', '')

        if download_excel:

            workbook = xlwt.Workbook()
            worksheet = workbook.add_sheet('report')
            style = xlwt.XFStyle()

            borders = xlwt.Borders()
            borders.bottom = xlwt.Borders.DASHED
            style.borders = borders

            column_length = len(required_columns)
            row_length = len(data_list) - 1
            # Writing headers first for the excel file.
            for column in range(column_length):
                worksheet.write(0, column, required_columns[column], style=style)
            # Writing rest of the rows.
            for row in range(1, row_length):
                for column in range(column_length):
                    worksheet.write(row, column, data_list[row][required_columns[column]], style=style)

            response = HttpResponse(mimetype='application/vnd.ms-excel', content_type='text/plain')
            start_date_string = datetime.datetime.fromtimestamp(float(start_date)).strftime("%d/%B/%Y")
            end_date_string = datetime.datetime.fromtimestamp(float(end_date)).strftime("%d/%B/%Y")
            response['Content-Disposition'] = 'attachment; filename=alert_report_{0}_{1}_to_{2}.xls' \
                .format(device_name, start_date_string, end_date_string)
            workbook.save(response)
            return response

        elif download_csv:

            response = HttpResponse(content_type='text/csv')
            start_date_string = datetime.datetime.fromtimestamp(float(start_date)).strftime("%d/%B/%Y")
            end_date_string = datetime.datetime.fromtimestamp(float(end_date)).strftime("%d/%B/%Y")
            response['Content-Disposition'] = 'attachment; filename=alert_report_{0}_{1}_to_{2}.csv' \
                .format(device_name, start_date_string, end_date_string)

            writer = csv.writer(response)
            headers = map(lambda x: x.replace('_', ' '), required_columns)
            writer.writerow(headers)
            column_length = len(required_columns)
            row_length = len(data_list) - 1

            for row in range(1, row_length):
                row_list = list()
                for column in range(0, column_length):
                    row_list.append(data_list[row][required_columns[column]])
                writer.writerow(row_list)
            return response

        else:

            required_columns = map(lambda x: x.replace('_', ' '), required_columns)
            context = dict(devices=devices_result,
                           current_device_id=device_id,
                           current_device_name=device_name,
                           page_type=page_type,
                           table_data=data_list,
                           table_header=required_columns,
                           service_name=service_name,
                           start_date_object=start_date_object,
                           end_date_object=end_date_object,
                           )

            return render(request, 'alert_center/single_device_alert.html', context)

    def get_result(self, page_type, organizations_ids):
        """
        Generic function to return the result w.r.t the page_type and organization of the current logged in user.

        :param page_type:
        :param organization:
        return result
        """

        if page_type == "customer" :
            substation_result = self.organization_customer_devices(organizations_ids)
            return substation_result
        elif page_type == "network":
            basestation_result = self.organization_network_devices(organizations_ids)
            return basestation_result


    def organization_customer_devices(self, organizations_ids):
        """
        To result back the all the customer devices from the respective organization..

        :param organization:
        :return list of customer devices
        """
        organization_customer_devices= Device.objects.filter(
                                       Q(sector_configured_on__isnull=False) | Q(substation__isnull=False),
                                       is_added_to_nms=1,
                                       is_deleted=0,
                                       organization__in=
                                       organizations_ids)
        result = list()
        for device in organization_customer_devices:
            result.append({'id': device.id, 'name':  device.device_name, 'alias': device.device_alias })

        return result

    def organization_network_devices(self, organizations_ids):
        """
        To result back the all the network devices from the respective organization..

        :param organization:
        :return list of network devices
        """
        organization_customer_devices= Device.objects.filter(
                                       ~Q(device_technology = int(P2P.ID)),
                                       is_added_to_nms=1,
                                       is_deleted=0,
                                       organization__in= organizations_ids)
        result = list()
        for device in organization_customer_devices:
            result.append({'id': device.id, 'name':  device.device_name, 'alias': device.device_alias })

        return result


# misc utility functions

def prepare_query(table_name=None,
                  devices=None,
                  data_sources=["pl", "rta"],
                  columns=None, condition=None,
                  offset=None,
                  limit=None):
    """

    :param table_name:
    :param devices:
    :param data_sources:
    :param columns:
    :param condition:
    :param offset:
    :param limit:
    :return:
    """
    in_string = lambda x: "'" + str(x) + "'"
    # col_string = lambda x,y: ("%s`" + str(x) + "`") %(y)
    query = None

    if not columns:
        return None

    if table_name and devices:
        query = "SELECT {0} FROM {1} as original_table " \
                "LEFT OUTER JOIN ({1} as derived_table) " \
                "ON ( " \
                "        original_table.data_source = derived_table.data_source " \
                "    AND original_table.device_name = derived_table.device_name " \
                "    AND original_table.id < derived_table.id" \
                ") " \
                "WHERE ( " \
                "        derived_table.id is null " \
                "    AND original_table.device_name in ( {2} ) " \
                "    {3}" \
                "    {4}" \
                ")" \
                "ORDER BY original_table.id DESC " \
                "".format(
            (',').join(["original_table.`" + col_name + "`" for col_name in columns]),
            table_name,
            (",".join(map(in_string, devices))),
            "AND original_table.data_source in ( {0} )".format(
                (',').join(map(in_string, data_sources))) if data_sources else "",
            condition.format("original_table") if condition else "",
            )
        if limit is not None and offset is not None:
            query += "LIMIT {0}, {1}".format(offset, limit)

    return query


def common_get_performance_data(model=EventNetwork,
                                table_name="performance_eventnetwork",
                                device_list=[],
                                data_sources_list=["pl", "rta"],
                                columns=None):
    """



    :param model:
    :param table_name:
    :param columns:
    :param data_sources_list:
    :param device_list:
    :return:
    """
    if not columns:
        columns = ["id", "service_name", "device_name", "data_source", "severity", "current_value", "sys_timestamp",
                   "description"]

    query = prepare_query(table_name=table_name,
                          devices=device_list,
                          data_sources=data_sources_list,
                          columns=columns
    )

    device_result = {}
    perf_result = {"severity": "N/A", "current_value": "N/A", "sys_timestamp": "N/A", "description": "N/A"}

    performance_data = model.objects.raw(query)

    for device in device_list:
        if device not in device_result:
            device_result[device] = perf_result

    for device in device_result:
        perf_result = {"severity": "N/A", "current_value": "N/A", "sys_timestamp": "N/A", "description": "N/A"}

        for data in performance_data:
            if str(data.device_name).strip().lower() == str(device).strip().lower():
                d_src = str(data.data_source).strip().lower()
                current_val = str(data.current_value)

                perf_result["severity"] = str(data.severity).strip().upper()

                perf_result["current_value"] = current_val

                perf_result["sys_timestamp"] = str(datetime.datetime.fromtimestamp(float(data.sys_timestamp)))

                perf_result["description"] = data.description

                device_result[device] = perf_result

    return device_result


def common_prepare_results(qs):
    """
    Common function to prepare result on query set

    :params qs:
    :return qs:
    """

    for dct in qs:
        if dct['severity'] == 'DOWN' or "CRITICAL" in dct['description'] or dct['severity'] == 'CRITICAL':
            dct['severity'] = '<i class="fa fa-circle red-dot" value="1" title="Critical"><span style="display:none">1</span></i>'
            dct['current_value'] = '<span class="text-danger">%s</span>' % (dct['current_value'])
            dct['description'] = '<span class="text-danger">%s</span>' % (dct['description'])

        elif dct['severity'] == 'WARNING' or "WARNING" in dct['description'] or "WARN" in dct['description']:
            dct['severity'] = '<i class="fa fa-circle orange-dot" value="2" title="Warning"><span style="display:none">2</span></i>'
            dct['current_value'] = '<span class="text-warning">%s</span>' % (dct['current_value'])
            dct['description'] = '<span class="text-warning">%s</span>' % (dct['description'])

        elif dct['severity'] == 'UP' or "OK" in dct['description']:
            dct['severity'] = '<i class="fa fa-circle green-dot" value="3" title="Ok"><span style="display:none">3</span></i>'
            dct['current_value'] = '<span class="text-success">%s</span>' % (dct['current_value'])
            dct['description'] = '<span class="text-success">%s</span>' % (dct['description'])

        else:
            dct['severity'] = '<i class="fa fa-circle grey-dot" value="4" title="Ok"><span style="display:none">4</span></i>'
            dct['current_value'] = '<span class="text-muted" >%s</span>' % (dct['current_value'])
            dct['description'] = '<span class="text-muted">%s</span>' % (dct['description'])

    return qs

def severity_level_check(list_to_check):
    """

    :return:
    """
    severity_check = ['DOWN', 'CRITICAL', 'WARNING', 'UNKNOWN', "WARN", "CRIT"]
    for item in list_to_check:
        for severity in severity_check:
            if severity in item:
                return True

def raw_prepare_result(performance_data,
                       machine,
                       table_name=None,
                       devices=None,
                       data_sources=["pl", "rta"],
                       columns=None,
                       condition=None,
                       offset=0,
                       limit=10
    ):
    """

    :param performance_data:
    :param machine:
    :param table_name:
    :param devices:
    :param data_sources:
    :param columns:
    :param condition:
    :param offset:
    :param limit:
    :return:
    """

    # count
    count = 0

    while count <= math.ceil(len(devices) / limit):

        query = prepare_query(table_name=table_name,
                              devices=devices[limit * count:limit * (count + 1)],# spilicing the devices here
                              data_sources=data_sources,
                              columns=columns,
                              condition=condition,
                              offset=offset,
                              limit=limit
        )
        # logger.debug(query)
        if query:
            performance_data += fetch_raw_result(query, machine)
        else:
            break

        count += 1

    return performance_data


def fetch_raw_result(query, machine):
    """
    django raw query does not get result in a single call, it iterates and calls the same query a lot of time
    which can be optmised if we pre fetch the results

    :param query: query to execute
    :param machine: machine name
    :return:the data fetched in form of a dictionary
    """

    cursor = connections[machine].cursor()
    cursor.execute(query)

    return dict_fetchall(cursor)


def dict_fetchall(cursor):
    """
    https://docs.djangoproject.com/en/1.6/topics/db/sql/
    return the cursor in dictionary format

    :param cursor: data base cursor
    :return: dictioanry of the rows
    """

    desc = cursor.description
    return [
        dict(zip([col[0] for col in desc], row))
        for row in cursor.fetchall()
    ]