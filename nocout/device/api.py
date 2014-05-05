import os, sys
import json
PROJ_PATH = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(PROJ_PATH)
os.environ['DJANGO_SETTINGS_MODULE'] = 'nocout.settings'

from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from django.views.generic.base import View
from django.http import HttpResponse
from django.contrib.auth.models import User
from user_profile.models import UserProfile, Department
from user_group.models import Organization
from device.models import Inventory, Device, DeviceType, DeviceVendor,\
                        DeviceTechnology, DeviceModel


class DeviceStatsApi(View):
    ''' Api calls initiated for device loc and stats'''

    def get(self, request):
        ''' Handling http GET method for device data'''

        req_params = request.GET
        host_ip = request.get_host().split(':')[0]
        self.false_response = {}
        self.true_response = {}
        self.true_response["success"] = 1
        self.true_response["message"] = "Device Data"
        self.false_response["success"] = 0
        self.false_response["message"] = "No Device Data"
        obj = DeviceStats()
        device_stats_list = obj.p2p_device_info(req_params.get('username'), host_ip)
        if device_stats_list:
            self.true_response["data"] = device_stats_list
            return HttpResponse(json.dumps(self.true_response))
        else:
            self.false_response["data"] = device_stats_list
            return HttpResponse(json.dumps(self.false_response))

class DeviceStats(View):
    ''' Class for Device stats methods'''

    def p2p_device_info(self, user, host_ip):
        ''' Getting P2P device stats associated with a particular user'''

        device_stats_list = []
        device_info_list = []
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
            device_info = {}
            try:
                device_object = Device.objects.get(id=dev_id.device_id)
            except ObjectDoesNotExist:
                print "No Device found"
                continue
            try:
                device_type_object = DeviceType.objects.get(id=device_object.device_type)
                device_type = device_type_object.name
            except ObjectDoesNotExist:
                print "No DeviceType found"
                device_type = None
            try:
                device_vendor_object = DeviceVendor.objects.get(id=device_object.device_vendor)
                device_vendor = device_vendor_object.name
            except ObjectDoesNotExist:
                print "No DeviceVendor found"
                device_vendor = None
            try:
                device_model_object = DeviceModel.objects.get(id=device_object.device_model)
                device_model = device_model_object.name
            except ObjectDoesNotExist:
                print "No DeviceModel found"
                device_model = None
            try:
                device_technology_object = DeviceTechnology.objects.get(id=device_object.device_technology)
                device_technology = device_technology_object.name
            except ObjectDoesNotExist:
                print "No DeviceTechnology found"
                device_technology = None
            try:
                device_info = {
                            "dev_id" : device_object.id, "name" : device_object.device_name, "alias" : \
                            device_object.device_alias, "type" : device_type, "mac" : \
                            device_object.mac_address, "current_state" : device_object.host_state, \
                            "vendor" : device_vendor, "model" : device_model,\
                            "technology" : device_technology,\
                            "parent_id" : device_object.parent_id, "lat" : device_object.latitude, \
                            "lon" : device_object.longitude, "markerUrl" : \
                            "http://%s:8000/static/img/marker/marker3.png" % host_ip, "perf" : "75%", "ip" : \
                            device_object.ip_address, "otherDetail" : "No Detail",\
                            "city" : device_object.city, "state" : device_object.state
                }
                device_info_list.append(device_info)
            except AttributeError, error:
                print "Device is None"
                print error
        
        for outer in device_info_list:
            for inner in device_info_list:
                if outer.get('parent_id') == inner.get('dev_id'):
                    ms_link = {"master" : inner, "slave" : outer, "link" : { "color" : "green"}}
                    device_stats_list.append(ms_link)

        return device_stats_list





