import json
import logging
import datetime
from django.db.models import Count
from django.db.models.query import ValuesQuerySet
from django.shortcuts import render_to_response
from django.views.generic import ListView
from django.template import RequestContext
from django_datatables_view.base_datatable_view import BaseDatatableView
from device.models import Device, City, State, DeviceTechnology
from inventory.models import BaseStation, Sector, SubStation, Circuit
from performance.models import PerformanceNetwork, EventNetwork, EventService, NetworkStatus

#sort the list of dictionaries
# http://stackoverflow.com/questions/72899/how-do-i-sort-a-list-of-dictionaries-by-values-of-the-dictionary-in-python
from operator import itemgetter


logger = logging.getLogger(__name__)


def getNetworkAlert(request):
    return render_to_response('alert_center/network_alerts_list.html', context_instance=RequestContext(request))


def getCustomerAlert(request, page_type="default_device_name"):
    if (page_type == "latency"):
        return render_to_response('alert_center/customer_latency_alerts_list.html',
                                  context_instance=RequestContext(request))
    else:
        return render_to_response('alert_center/customer_packet_alerts_list.html',
                                  context_instance=RequestContext(request))


def getCustomerAlertDetail(request):
    return render_to_response('alert_center/customer_details_list.html', context_instance=RequestContext(request))


def getNetworkAlertDetail(request):
    return render_to_response('alert_center/network_details_list.html', context_instance=RequestContext(request))


# **************************************** Latency *********************************************
class AlertCenterNetworkListing(ListView):
    model = EventNetwork
    template_name = 'alert_center/network_alerts_list.html'

    def get_context_data(self, **kwargs):
        context = super(AlertCenterNetworkListing, self).get_context_data(**kwargs)
        datatable_headers_latency = [

            {'mData': 'severity', 'sTitle': '', 'sWidth': '40px', 'bSortable': False},
            {'mData': 'device_name', 'sTitle': 'Device Name', 'sWidth': 'null', 'sClass': 'hidden-xs',
             'bSortable': False},
            {'mData': 'ip_address', 'sTitle': 'IP Address', 'sWidth': 'null', 'sClass': 'hidden-xs',
             'bSortable': False},
            {'mData': 'base_station', 'sTitle': 'Base Station', 'sWidth': 'null', 'sClass': 'hidden-xs',
             'bSortable': False},
            {'mData': 'base_station__city', 'sTitle': 'City', 'sWidth': 'null', 'sClass': 'hidden-xs',
             'bSortable': False},
            {'mData': 'base_station__state', 'sTitle': 'State', 'sWidth': 'null', 'sClass': 'hidden-xs',
             'bSortable': False},
            {'mData': 'current_value', 'sTitle': 'Latency', 'sWidth': 'null', 'sClass': 'hidden-xs',
             'bSortable': False},
            {'mData': 'description', 'sTitle': 'Alert Description', 'sWidth': 'null', 'bSortable': False},
            {'mData': 'sys_timestamp', 'sTitle': 'Timestamp', 'sWidth': 'null', 'bSortable': False}, ]

        datatable_headers_packetdrop = [
            {'mData': 'severity', 'sTitle': '', 'sWidth': '40px', 'bSortable': False},
            {'mData': 'device_name', 'sTitle': 'Device Name', 'sWidth': 'null', 'sClass': 'hidden-xs',
             'bSortable': False},
            {'mData': 'ip_address', 'sTitle': 'IP Address', 'sWidth': 'null', 'sClass': 'hidden-xs',
             'bSortable': False},
            {'mData': 'base_station', 'sTitle': 'Base Station', 'sWidth': 'null', 'sClass': 'hidden-xs',
             'bSortable': False},
            {'mData': 'base_station__city', 'sTitle': 'City', 'sWidth': 'null', 'sClass': 'hidden-xs',
             'bSortable': False},
            {'mData': 'base_station__state', 'sTitle': 'State', 'sWidth': 'null', 'sClass': 'hidden-xs',
             'bSortable': False},
            {'mData': 'current_value', 'sTitle': 'Packet Drop', 'sWidth': 'null', 'sClass': 'hidden-xs',
             'bSortable': False},
            {'mData': 'description', 'sTitle': 'Event Description', 'sWidth': 'null', 'bSortable': False},
            {'mData': 'sys_timestamp', 'sTitle': 'Timestamp', 'sWidth': 'null', 'bSortable': False},
        ]
        datatable_headers_down = [
            {'mData': 'severity', 'sTitle': '', 'sWidth': '40px', 'bSortable': False},
            {'mData': 'device_name', 'sTitle': 'Device Name', 'sWidth': 'null', 'sClass': 'hidden-xs',
             'bSortable': False},
            {'mData': 'ip_address', 'sTitle': 'IP Address', 'sWidth': 'null', 'sClass': 'hidden-xs',
             'bSortable': False},
            {'mData': 'base_station', 'sTitle': 'Base Station', 'sWidth': 'null', 'sClass': 'hidden-xs',
             'bSortable': False},
            {'mData': 'base_station__city', 'sTitle': 'City', 'sWidth': 'null', 'sClass': 'hidden-xs',
             'bSortable': False},
            {'mData': 'base_station__state', 'sTitle': 'State', 'sWidth': 'null', 'sClass': 'hidden-xs',
             'bSortable': False},
            {'mData': 'current_value', 'sTitle': 'Packet Drop', 'sWidth': 'null', 'sClass': 'hidden-xs',
             'bSortable': False},
            {'mData': 'description', 'sTitle': 'Event Description', 'sWidth': 'null', 'bSortable': False},
            {'mData': 'sys_timestamp', 'sTitle': 'Timestamp', 'sWidth': 'null', 'bSortable': False},
        ]
        datatable_headers_servicealerts = [
            {'mData': 'severity', 'sTitle': '', 'sWidth': '40px', 'bSortable': False},
            {'mData': 'device_name', 'sTitle': 'Device Name', 'sWidth': 'null', 'sClass': 'hidden-xs',
             'bSortable': False},
            {'mData': 'ip_address', 'sTitle': 'IP Address', 'sWidth': 'null', 'sClass': 'hidden-xs',
             'bSortable': False},
            {'mData': 'base_station', 'sTitle': 'Base Station', 'sWidth': 'null', 'sClass': 'hidden-xs',
             'bSortable': False},
            {'mData': 'base_station__city', 'sTitle': 'City', 'sWidth': 'null', 'sClass': 'hidden-xs',
             'bSortable': False},
            {'mData': 'base_station__state', 'sTitle': 'State', 'sWidth': 'null', 'sClass': 'hidden-xs',
             'bSortable': False},
            {'mData': 'current_value', 'sTitle': 'Packet Drop', 'sWidth': 'null', 'sClass': 'hidden-xs',
             'bSortable': False},
            {'mData': 'description', 'sTitle': 'Event Description', 'sWidth': 'null', 'bSortable': False},
            {'mData': 'sys_timestamp', 'sTitle': 'Timestamp', 'sWidth': 'null', 'bSortable': False},
        ]
        context['datatable_headers_servicealerts'] = json.dumps(datatable_headers_servicealerts)
        context['datatable_headers_down'] = json.dumps(datatable_headers_down)
        context['datatable_headers_packetdrop'] = json.dumps(datatable_headers_packetdrop)
        context['datatable_headers_latency'] = json.dumps(datatable_headers_latency)
        return context


class AlertCenterNetworkListingTable(BaseDatatableView):
    model = EventNetwork
    columns = ['device_name', 'machine_name', 'site_name', 'ip_address', 'severity',
               'current_value', 'sys_timestamp', 'description']
    order_columns = ['device_name', 'machine_name', 'site_name', 'ip_address', 'severity',
                     'current_value', 'sys_timestamp', 'description']

    def filter_queryset(self, qs):

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
        if not self.model:
            raise NotImplementedError("Need to provide a model or implement get_initial_queryset!")

        logged_in_user = self.request.user.userprofile

        if logged_in_user.role.values_list('role_name', flat=True)[0] == 'admin':
            organizations = list(logged_in_user.organization.get_children()) + [logged_in_user.organization]
        else:
            organizations = [logged_in_user.organization]
        sector_configured_on_devices_ids = list()

        for organization in organizations:
            sector_configured_on_devices_ids += Sector.objects.filter(
                sector_configured_on__id__in=organization.device_set \
                .values_list('id', flat=True)).values_list('sector_configured_on', flat=True).annotate(
                dcount=Count('base_station'))

        sector_configured_on_devices_name = Device.objects.filter(is_added_to_nms=1,
                                                                  id__in=sector_configured_on_devices_ids) \
            .values_list('device_name', flat=True)

        device_list, performance_data, data_sources_list = list(), list(), list()
        extra_query_condition=None

        if 'latency' in self.request.path_info:
            data_sources_list.append('rta')
        elif 'packetdrop' in self.request.path_info:
            data_sources_list.append('pl')
        elif 'down' in self.request.path_info:
            data_sources_list.append('pl')
            extra_query_condition="AND (`{0}`.`current_value` = 100 OR `{0}`.`severity`='DOWN' ) "
        elif 'service' in self.request.path_info:
            return device_list

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

        query = prepare_query(table_name="performance_eventnetwork", devices=sector_configured_on_devices_name, \
                              data_sources=data_sources_list, columns=required_data_columns, condition=extra_query_condition)

        if query:
            performance_data = self.model.objects.raw(query)

            device_data= list()

            for data in performance_data:
                device_base_station= Sector.objects.get( sector_configured_on__id=Device.objects.get(device_name=\
                                     data.device_name).id).base_station
                ddata = {
                        'device_name':data.device_name,
                        'severity':data.severity,
                        'ip_address':data.ip_address,
                        'base_station':device_base_station.name,
                        'base_station__city':City.objects.get(id=device_base_station.city).city_name,
                        'base_station__state':State.objects.get(id=device_base_station.state).state_name,
                        'current_value':data.current_value,
                        'sys_timestamp':str(datetime.datetime.fromtimestamp(float( data.sys_timestamp ))),
                        'description':data.description
                        }
                device_data.append(ddata)


            sorted_device_data = sorted(device_data, key=itemgetter('sys_timestamp'), reverse=True)
            return sorted_device_data

        return device_list

    def prepare_results(self, qs):

        if qs:
            qs = [ { key: val if val else "" for key, val in dct.items() } for dct in qs ]

        return common_prepare_results(qs)

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
    model = EventNetwork
    template_name = 'alert_center/customer_alerts_list.html'

    def get_context_data(self, **kwargs):
        context = super(CustomerAlertList, self).get_context_data(**kwargs)
        datatable_headers = [
            {'mData': 'severity', 'sTitle': '', 'sWidth': '40px', 'bSortable': False},
            {'mData': 'device_name', 'sTitle': 'Device Name', 'sWidth': 'null', 'sClass': 'hidden-xs',
             'bSortable': False},
            {'mData': 'ip_address', 'sTitle': 'IP', 'sWidth': 'null', 'sClass': 'hidden-xs', 'bSortable': False},
            {'mData': 'sub_station', 'sTitle': 'Sub Station', 'sWidth': 'null', 'sClass': 'hidden-xs',
             'bSortable': False},
            {'mData': 'sub_station__city', 'sTitle': 'City', 'sWidth': 'null', 'sClass': 'hidden-xs',
             'bSortable': False},
            {'mData': 'sub_station__state', 'sTitle': 'State', 'sWidth': 'null', 'sClass': 'hidden-xs',
             'bSortable': False},
            {'mData': 'base_station', 'sTitle': 'Base Station', 'sWidth': 'null', 'sClass': 'hidden-xs',
             'bSortable': False},
            {'mData': 'current_value', 'sTitle': 'Event Value', 'sWidth': 'null', 'sClass': 'hidden-xs',
             'bSortable': False},
            {'mData': 'description', 'sTitle': 'Event Description', 'sWidth': 'null', 'bSortable': False},
            {'mData': 'sys_timestamp', 'sTitle': 'Timestamp', 'sWidth': 'null', 'bSortable': False},
        ]
        context['datatable_headers'] = json.dumps(datatable_headers)
        context['data_source'] = " ".join(self.kwargs['data_source'].split('_')).title()
        return context


class CustomerAlertListingTable(BaseDatatableView):
    model = EventNetwork
    columns = ['device_name', 'machine_name', 'site_name', 'ip_address', 'severity',
               'current_value', 'sys_timestamp', 'description']
    order_columns = ['device_name', 'machine_name', 'site_name', 'ip_address', 'severity',
                      'current_value', 'sys_timestamp', 'description']

    def filter_queryset(self, qs):

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
        if not self.model:
            raise NotImplementedError("Need to provide a model or implement get_initial_queryset!")

        logged_in_user = self.request.user.userprofile

        if logged_in_user.role.values_list('role_name', flat=True)[0] == 'admin':
            organizations = list(logged_in_user.organization.get_children()) + [logged_in_user.organization]
        else:
            organizations = [logged_in_user.organization]

        organization_devices = list()
        device_tab_technology = self.request.GET.get('data_tab')
        device_technology_id= DeviceTechnology.objects.get(name=device_tab_technology).id
        for organization in organizations:
            organization_devices += Device.objects.filter(is_added_to_nms=1, organization__id=organization.id,
                                                          device_technology=device_technology_id)
            # get the devices in an organisation which are added for monitoring

        organization_substations_devices_name = [device.device_name for device in organization_devices if
                                                 device.substation_set.exists()]

        device_list, performance_data = list(), list()

        data_sources_list = list()

        if self.request.GET['data_source'] == 'latency':
            data_sources_list.append('rta')
        elif self.request.GET['data_source'] == 'packet_drop':
            data_sources_list.append('pl')

        required_data_columns = ["id",
                                 "data_source",
                                 "device_name",
                                 "severity",
                                 "current_value",
                                 "sys_timestamp",
                                 "description"
        ]

        query = prepare_query(table_name="performance_eventnetwork", devices=organization_substations_devices_name, \
                              data_sources=data_sources_list, columns=required_data_columns)

        if query:
            performance_data = self.model.objects.raw(query)

        for data in performance_data:
            for device in organization_substations_devices_name:
                if device == data.device_name:
                    device_substation = SubStation.objects.get(device__device_name=device)
                    try:
                        #try exception if the device does not have any association with the circuit
                        device_substation_base_station= Circuit.objects.get(sub_station__id= device_substation.id).sector.base_station
                        device_substation_base_station_name= device_substation_base_station.name
                    except:
                        device_substation_base_station_name='N/A'
                    device_events = {
                        'device_name': device,
                        'severity': data.severity,
                        'ip_address': Device.objects.get(device_name=device).ip_address,
                        'sub_station': device_substation.name,
                        'sub_station__city': City.objects.get(id=device_substation.city).city_name,
                        'sub_station__state': State.objects.get(id=device_substation.state).state_name,
                        'base_station':device_substation_base_station_name,
                        'current_value': data.current_value,
                        'sys_timestamp': str(datetime.datetime.fromtimestamp(float( data.sys_timestamp ))),
                        'description':data.description
                    }
                    device_list.append(device_events)
                else:
                    continue
        sorted_device_list = sorted(device_list, key=itemgetter('sys_timestamp'), reverse=True)
        return sorted_device_list

    def prepare_results(self, qs):

        if qs:
            qs = [ { key: val if val else "" for key, val in dct.items() } for dct in qs ]

        return common_prepare_results(qs)


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


# misc utility functions

def prepare_query(table_name=None, devices=None, data_sources=["pl", "rta"], columns=None, condition=None):
    in_string = lambda x: "'" + str(x) + "'"
    # col_string = lambda x,y: ("%s`" + str(x) + "`") %(y)
    query = None

    if not columns:
        return None

    extra_where_clause = condition if condition else ""
    if table_name and devices:
        query = "SELECT {0} FROM {1} as original_table " \
                "INNER JOIN ({1} as derived_table) " \
                "ON ( " \
                "    original_table.data_source = derived_table.data_source AND " \
                "    original_table.device_name = derived_table.device_name AND " \
                "    original_table.id < derived_table.id" \
                ") " \
                "WHERE ( " \
                "    original_table.device_name in ( {2} ) AND " \
                "    original_table.data_source in ( {3} )" \
                "    {4}" \
                ")" \
                "GROUP BY original_table.device_name, original_table.data_source " \
                "" \
                "ORDER BY derived_table.id DESC" \
                "".format(
                    (',').join(["derived_table.`" + col_name + "`" for col_name in columns]),
                    table_name,
                    (",".join(map(in_string, devices))),
                    (',').join(map(in_string, data_sources)),
                    extra_where_clause.format("derived_table")
                )

    # logger.debug(query)

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
        columns = ["id", "service_name", "device_name", "data_source", "severity", "current_value", "sys_timestamp", "description"]


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

    for dct in qs:
        if dct['severity']=='DOWN':
           dct['severity']='<div class="alert_critical"></div>'
           dct['current_value']='<span class="text-danger">%s</span>'%(dct['current_value'])
           dct['description']='<span class="text-danger">%s</span>'%(dct['description'])

        elif dct['severity']=='CRITICAL':
            dct['severity']='<div class="alert_critical"></div>'
            dct['current_value']='<span style="color:#d9534f">%s</span>'%(dct['current_value'])
            dct['description']='<span style="color:#d9534f">%s</span>'%(dct['description'])

        elif dct['severity']=='WARNING':
            dct['severity']='<div class="alert_major"></div>'
            dct['current_value']='<span style="color:#FFA500">%s</span>'%(dct['current_value'])
            dct['description']='<span style="color:#FFA500">%s</span>'%(dct['description'])

        elif dct['severity']=='UP':
            dct['severity']='<div class="alert_normal"></div>'
            dct['current_value']='<span style="color:#008000">%s</span>'%(dct['current_value'])
            dct['description']='<span style="color:#008000">%s</span>'%(dct['description'])

        else:
            dct['severity']='<div class="alert_informational"></div>'
            dct['current_value']='<span style="color:#bba11f" >%s</span>'%(dct['current_value'])
            dct['description']='<span style="color:#bba11f">%s</span>'%(dct['description'])

    return qs
