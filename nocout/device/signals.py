"""
Module which defines signals.
"""
from django.db.models.loading import get_model

def update_device_type_service(sender, instance=None, created=False, **kwargs):
    """
    If a new device type service is created auto assign default data source of service to it.
    """
    DeviceTypeServiceDataSource = get_model('device', 'DeviceTypeServiceDataSource', seed_cache=True)
    ServiceSpecificDataSource = get_model('service', 'ServiceSpecificDataSource', seed_cache=True)

    DeviceTypeServiceDataSource.objects.filter(device_type_service=instance).delete()

    dt_sds = list()
    service_ds = ServiceSpecificDataSource.objects.filter(service=instance.service)
    for ds in service_ds:
        kwargs=dict(device_type_service=instance,
                    service_data_sources=ds.service_data_sources,
                    warning=ds.warning,
                    critical=ds.critical)
        dt_sds.append(DeviceTypeServiceDataSource(**kwargs))

    DeviceTypeServiceDataSource.objects.bulk_create(dt_sds)

