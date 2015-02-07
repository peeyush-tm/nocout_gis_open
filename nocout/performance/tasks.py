from celery import task
from device.models import Device
from performance.views import device_last_down_time
from device.models import DeviceType

@task()
def device_last_down_time_task(device_type=None):
    """

    :param device_type: can be
     MariaDB [nocout_m5]> select name, id from device_devicetype;
                            +---------------+----+
                            | name          | id |
                            +---------------+----+
                            | CanopyPM100AP |  6 | --> added
                            | CanopyPM100SS |  7 | --> added
                            | CanopySM100AP |  8 | --> added
                            | CanopySM100SS |  9 | --> added
                        | Converter     | 15 |
                            | Default       |  1 | --> DON'T ADD
                        | PINE          | 13 |
                            | Radwin2KBS    |  3 | --> added
                            | Radwin2KSS    |  2 | --> added
                        | RiCi          | 14 |
                            | StarmaxIDU    |  4 | --> added
                            | StarmaxSS     |  5 | --> added
                        | Switch        | 12 |
                            +---------------+----+
    :return: True
    """
    devices = Device.objects.filter(is_added_to_nms=1)
    try:
        if device_type:
            dtype = DeviceType.objects.filter(name=device_type).get().id
            devices = devices.filter(device_type=dtype)
    except:
        pass

    for device_object in devices:
        x = device_last_down_time(device_object=device_object)
    return True