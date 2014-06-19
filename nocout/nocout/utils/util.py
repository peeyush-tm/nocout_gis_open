import datetime

#Used for JsonDatetime Encoding #example# ::json.dumps( json_object, default=date_handler )
from device.models import Device
from device_group.models import DeviceGroup
from user_group.models import UserGroup

date_handler = lambda obj: obj.strftime('%Y-%m-%d %H:%M:%S') if isinstance(obj, datetime.datetime) else None


class DictDiffer(object):
    """
    Calculate the difference between two dictionaries as:
    (1) items added
    (2) items removed
    (3) keys same in both but changed values
    (4) keys same in both and unchanged values
    """
    def __init__(self, current_dict, past_dict):
        self.current_dict, self.past_dict = current_dict, past_dict
        self.set_current, self.set_past = set(current_dict.keys()), set(past_dict.keys())
        self.intersect = self.set_current.intersection(self.set_past)
    def added(self):
        return self.set_current - self.intersect
    def removed(self):
        return self.set_past - self.intersect
    def changed(self):
        return set(o for o in self.intersect if self.past_dict[o] != self.current_dict[o])
    def unchanged(self):
        return set(o for o in self.intersect if self.past_dict[o] == self.current_dict[o])


class Logged_In_User_Devices:
    """
    The Class is used to return the number of the devices for the Logged in User.

    """
    def __init__(self, request, columns):
        self.request=request #request object
        self.columns=columns #column names

    def logged_in_user_devices_query(self):
        user_group = UserGroup.objects.get( pk__in = self.request.user.userprofile.user_group.values_list('id', flat=True))
        device_group_list = DeviceGroup.objects.filter( pk__in = user_group.device_group.values_list('id', flat=True))
        return Device.objects.filter(device_group__in = device_group_list ).values(*self.columns)
