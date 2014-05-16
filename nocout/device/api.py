import json
import copy
from django.core.exceptions import ObjectDoesNotExist
from django.views.generic.base import View
from django.http import HttpResponse
from django.contrib.auth.models import User
from user_profile.models import Department
from user_group.models import Organization
from device.models import Inventory, Device, DeviceType, DeviceVendor, \
    DeviceTechnology, DeviceModel


class DeviceStatsApi(View):
    """
    Api calls initiated for device stats

    """
    
    def get(self, request):
        """
        Handling http GET method for device data

        Args:
            request (WSGIRequest): The request object.

        Returns:
            {
                'success': 1,
                'message': 'Device Data',
                'object': device stats `dict` object
            }

        """

        req_params = request.GET
        if 'username' in req_params:
            #Get username from query string, if passed
            username = req_params.get('username')
        else:
            #Retreive username from active session
            username = request.user.username
        #Get the host machine IP address
        host_ip = request.get_host().split(':')[0]
        #Show link between master-slave device pairs
        show_link = 1
        #Result dict prototype
        self.result = {
            "success": 0,
            "message": "No Device Data",
            "data": {
                "meta": None,
                "objects": None
            }
        }
        cls = DeviceStats()
        device_stats_dict = DeviceStats.p2p_device_info(
            cls,
            username,
            host_ip,
            show_link
        )

        if len(device_stats_dict.get('children')):
            self.result.update({
                "success": 1,
                "message": "Device Data",
                "data": {
                    "meta": None,
                    "objects": device_stats_dict
                }
            })
            return HttpResponse(json.dumps(self.result),
                    mimetype="application/json")
        else:
            return HttpResponse(json.dumps(self.result))


class DeviceStats(View):
    """
    Base class for Device stats methods
    """

    def p2p_device_info(self, user, host_ip, show_link):
        """
        Serves device stats data for devices associated
        with a particular user

        Args:
            user (str): Username passed in the querystring.
            host_ip (str): IP address of the host machine.
            show_link (int): Would show the links on GIS, 
                if value goes to 1.

        Returns:
            Device stats `dict` object.
        
        """

        #Prototype for device dict
        device_stats_dict = {
            "id": "root node",
            "name": "Root Site Instance",
            "data": {
                "$type": "none"
            },
            "children": []
        }
        device_info_list = []
        device_object_list = []
        try:
            self.user_id = User.objects.get(username=user).id
            self.user_gp_id = Department.objects.get(
                user_profile_id=self.
                user_id
            ).user_group_id
            self.dev_gp_id = Organization.objects.get(
                user_group_id=self.
                user_gp_id
            ).device_group_id
            inventory_list = Inventory.objects.filter(
                device_group_id=self.
                dev_gp_id
            ).values()
        except Exception, error:
            print "No Data for this user"
            return device_stats_dict

        meta_info={"page_number": 4, "limit": 2}
        inventory_list = self.slice_object_list(inventory_list, meta_info)

        for dev in inventory_list:
            device_info = {}
            try:
                if not [d.id for d in device_object_list if d.id == dev.get('device_id')]:
                    device_object = Device.objects.get(
                        id=dev.get('device_id')
                    )
                    print "--Device Object--"
                    print device_object
                    device_object_list.append(device_object)
                if not [d.id for d in device_object_list if d.id == device_object.parent_id]:
                    master_device_object = Device.objects.get(
                        id=device_object.parent_id
                    )
                    print "--Master Device Object--"
                    print master_device_object
                    device_object_list.append(master_device_object)
            except ObjectDoesNotExist:
                print "No Device found"
                continue

        for obj in device_object_list:
            try:
                device_type_object = DeviceType.objects.get(
                    id=obj.device_type
                )
                device_type = device_type_object.name
            except ObjectDoesNotExist:
                print "No DeviceType found"
                device_type = None
            try:
                device_vendor_object = DeviceVendor.objects.get(
                    id=obj.device_vendor
                )
                device_vendor = device_vendor_object.name
            except ObjectDoesNotExist:
                print "No DeviceVendor found"
                device_vendor = None
            try:
                device_model_object = DeviceModel.objects.get(
                    id=obj.device_model
                )
                device_model = device_model_object.name
            except ObjectDoesNotExist:
                print "No DeviceModel found"
                device_model = None
            try:
                device_technology_object = DeviceTechnology.objects.get(
                    id=obj.device_technology
                )
                device_technology = device_technology_object.name
            except ObjectDoesNotExist:
                print "No DeviceTechnology found"
                device_technology = None
            try:
                device_info = {
                    "id": obj.id,
                    "name": obj.device_name,
                    "alias": obj.device_alias,
                    "device_type": device_type,
                    "mac": obj.mac_address,
                    "current_state": obj.host_state,
                    "vendor": device_vendor,
                    "model": device_model,
                    "technology": device_technology,
                    "parent_id": obj.parent_id,
                    "lat": obj.latitude,
                    "lon": obj.longitude,
                    "markerUrl": "http://%s:8000/static/img/marker/marker3.png"
                    % host_ip, "perf": "75%",
                    "ip": obj.ip_address,
                    "otherDetail": "No Detail",
                    "city": obj.city,
                    "state": obj.state
                }
                device_info_list.append(device_info)
            except AttributeError, error:
                print "Device Info key error"
                print error

        print "-- Complete Device Info List --"
        print device_info_list
        

        #Master-slave pairs based on `parent_id` and `device_id`
        for outer in device_info_list:
            master = copy.deepcopy(outer)
            master.update(
                {
                "showLink": show_link,
                "children": []
                }
            )
            #dict to store master device info
            master = {
                "id": master.pop('id'),
                "parent_id": master.pop('parent_id'),
                "name": master.pop('name'),
                "children": master.pop('children'),
                "data": master
            }
            for inner in device_info_list:
                if inner.get('parent_id') == outer.get('id'):
                    slave = copy.deepcopy(inner)
                    slave.update(
                        {
                        "linkColor": "green",
                        "children": []
                        }
                    )
                    #dict to store slave device info
                    slave = {
                        "id": slave.pop('id'),
                        "name": slave.pop('name'),
                        "parent_id": slave.pop('parent_id'),
                        "children": slave.pop('children'),
                        "data": slave
                    }
                    master.pop('parent_id', None)
                    slave.pop('parent_id', None)
                    master.get('children').append(slave)
                    device_stats_dict.get('children').append(master)

        return device_stats_dict


    def slice_object_list(self, inventory_list, meta_info):
        print meta_info
        start = int(meta_info.get('limit')) * \
            int(meta_info.get('page_number', 0)-1)
        end = int(meta_info.get('limit')) * \
            int(meta_info.get('page_number', 0))
        print start, end
        inventory_list = inventory_list[start:end]
        return inventory_list
