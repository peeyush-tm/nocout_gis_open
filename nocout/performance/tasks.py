from celery import task
from device.models import Device
from performance.views import device_last_down_time

@task()
def device_last_down_time_task():
    devices = Device.objects.filter(is_added_to_nms=1)
    for device_object in devices:
        x = device_last_down_time(device_object=device_object)
    return True