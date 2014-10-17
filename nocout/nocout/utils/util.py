import datetime

#Used for JsonDatetime Encoding #example# ::json.dumps( json_object, default=date_handler )
from django.contrib.auth.models import User
from device.models import Device
from device_group.models import DeviceGroup
from organization.models import Organization
from user_group.models import UserGroup
from user_profile.models import UserProfile
from random import randint, uniform

from django.db import connections

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


project_group_role_dict_mapper={
    'admin':'group_admin',
    'operator':'group_operator',
    'viewer':'group_viewer',
}

#code duplication
def fetch_raw_result(query, machine='default'):
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

#duplicate code: TODO : remove

def format_value(format_this, type_of=None):
    """

    :param format_this:
    :return:
    """
    try:
        if not type_of:
            return format_this if format_this else 'NA'
        elif type_of == 'frequency_color':
            return format_this if format_this else 'rgba(74,72,94,0.58)'
        elif type_of == 'frequency_radius':
            return format_this if format_this else uniform(0,3)
        elif type_of == 'integer':
            return format_this if format_this else 0
        elif type_of == 'antenna':
            return format_this if format_this else 'vertical'
        elif type_of == 'random':
            return format_this if format_this else randint(40,70)
        elif type_of == 'icon':
            if len(str(format_this)) > 5:
                img_url = str("media/"+ str(format_this)) \
                    if "uploaded" in str(format_this) \
                    else "static/img/" + str(format_this)
                return img_url
            else:
                return "static/img/icons/mobilephonetower10.png"
    except:
        pass
    return 'NA'