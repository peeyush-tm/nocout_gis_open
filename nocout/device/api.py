import os, sys
import json
PROJ_PATH = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(PROJ_PATH)
os.environ['DJANGO_SETTINGS_MODULE'] = 'nocout.settings'

from django.conf import settings
from django.core import serializers
from django.views.generic.base import View
from django.http import HttpResponse
from django.contrib.auth.models import User
from user_profile.models import UserProfile, Department
from user_group.models import Organization
from device.models import Inventory, Device


class DeviceStatsApi(View):
    ''' Api calls initiated for device loc and stats'''

    def get(self, request):
        ''' Handling http GET method for device data'''

        req_params = request.GET
        self.false_response = {}
        self.true_response = {}
        self.true_response["success"] = 1
        self.true_response["message"] = "Device Data"
        self.false_response["success"] = 0
        self.false_response["message"] = "No Device Data"
        obj = DeviceStats()
        device_stats_list = obj.p2p_device_info(req_params.get('username'))
        if device_stats_list:
            self.true_response["data"] = device_stats_list
            return HttpResponse(json.dumps(self.true_response))
        else:
            self.false_response["data"] = device_stats_list
            return HttpResponse(json.dumps(self.false_response))

class DeviceStats(View):
    ''' Class for Device stats methods'''

    def p2p_device_info(self, user):
        ''' Getting P2P device stats associated with a particular user'''

        device_stats_list = []
        try:
            self.user_id = User.objects.get(username=user).id
            self.user_gp_id = Department.objects.get(user_profile_id=self.user_id).\
                                                    user_group_id
            self.dev_gp_id = Organization.objects.get(user_group_id=self.user_gp_id).\
                                                    device_group_id
            device_id_list = Inventory.objects.filter(device_group_id=self.dev_gp_id)
        except Exception, error:
            print "No Data for this user"
            return device_stats_list

        for dev_id in device_id_list:
            device_data = {}
            slave_info = Device.objects.get(id=dev_id.device_id)
            parent_id = slave_info.parent_id
            #device_data = serializers.serialize('json', [info])
            #device_stats_list.append(device_data)
            slave_device = {
                        "name" : slave_info.device_name, "alias" : slave_info.device_alias, \
                        "type" : slave_info.device_type, "mac" : slave_info.mac_address, \
                        "current_state" : slave_info.host_state,\
                        "lat" : slave_info.latitude, "lon" : slave_info.longitude,\
                        "markerUrl" : "", "perf" : "75%", "ip" : slave_info.ip_address,\
                        "otherDetail" : "No Detail"
            }
            master_info = Device.objects.get(id=parent_id)
            master_device = {       
                        "name" : master_info.device_name, "alias" : master_info.device_alias,\
                        "type" : master_info.device_type, "mac" : master_info.mac_address,\
                        "current_state" : master_info.host_state, "lat" : master_info.latitude,\
                        "lon" : master_info.longitude, "markerUrl" : "", "perf" : "75%",\
                        "ip" : master_info.ip_address, "otherDetail" : "No Detail"
            }
            ms_link = {"master" : master_device, "slave" : slave_device, "link" : { "color" : "green"}}

            device_stats_list.append(ms_link)

        return device_stats_list





