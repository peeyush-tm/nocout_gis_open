# -*- encoding: utf-8; py-indent-offset: 4 -*-

from celery import task, group
from device.models import Device
from performance.views import device_last_down_time
from device.models import DeviceType, SiteInstance

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
    g_jobs = list()
    ret = False

    #devices = Device.objects.filter(is_added_to_nms=1)
    #logger.debug(devices)
    devices = None
    try:
        if device_type:
            dtype = DeviceType.objects.filter(name=device_type).get().id
            devices = Device.objects.filter(is_added_to_nms=1, device_type=dtype)
    except Exception as e:
        return ret

    sites = SiteInstance.objects.all().values_list('name', flat=True)

    for site in sites:
        if devices:
            site_devices = devices.filter(site_instance__name=site)
            if site_devices and site_devices.count():
                g_jobs.append(device_last_down_time_site_wise.s(devices=site_devices))
        else:
            continue

    if len(g_jobs):
        job = group(g_jobs)
        result = job.apply_async()
        for r in result.get():
            ret |= r

    return ret


@task()
def device_last_down_time_site_wise(devices):
    """
    collect device information per site wise
    :return: True
    """
    if devices and devices.count():
        for device_object in devices:
            x = device_last_down_time(device_object=device_object)
        return True
    else:
        return False