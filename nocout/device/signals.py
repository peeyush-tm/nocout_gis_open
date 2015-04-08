"""
Module which defines signals.
"""
from django.db.models.loading import get_model


def update_site_on_device_change(sender, instance=None, created=False, **kwargs):
    """
        Set 'is_device_change' in site instance to 1 if device name, site or ip address in device created or modified
        Parameters:
            - sender (<class 'mptt.models.MPTTModelBase'>) - sender model class i.e. <class 'device.models.Device'>
            - instance (<class 'device.models.Device'>) - instance being saved for e.g. Default
            - created (bool) - object created or updated
            - kwargs (dict) - a dictionary of keyword arguments passed to constructor for e.g.
                                {
                                    'update_fields': None,
                                    'raw': False,
                                    'signal': <django.dispatch.dispatcher.Signalobjectat0x7f44749958d0>,
                                    'using': 'default'
                                }
    """

    # import model inside function to avoid circular dependency
    from device.models import Device

    # instance before saving the form
    old_instance = None
    try:
        old_instance = Device.objects.get(id=instance.id)
    except Exception as e:
        pass

    if old_instance:
        # old fields values list
        old_values = [old_instance.device_name,
                      old_instance.ip_address,
                      old_instance.site_instance.name,
                      old_instance.host_state]

        # new fields values list
        new_values = [instance.device_name,
                      instance.ip_address,
                      instance.site_instance.name,
                      instance.host_state]

        if instance.site_instance.is_device_change != 1:
            if list(set(old_values) - set(new_values)):
                instance.site_instance.is_device_change = 1
                instance.site_instance.save()
                if instance.site_instance != old_instance.site_instance:
                    old_instance.site_instance.is_device_change = 1
                    old_instance.site_instance.save()
    else:
        instance.site_instance.is_device_change = 1
        instance.site_instance.save()


def update_site_on_devicetype_change(sender, instance=None, created=False, **kwargs):
    """
        Set 'is_device_change' in site instance to 1 if device name, site or ip address in device created or modified
        Parameters:
            - sender (<class 'mptt.models.MPTTModelBase'>) - sender model class i.e. <class 'device.models.Device'>
            - instance (<class 'device.models.Device'>) - instance being saved for e.g. Default
            - created (bool) - object created or updated
            - kwargs (dict) - a dictionary of keyword arguments passed to constructor for e.g.
                                {
                                    'update_fields': None,
                                    'raw': False,
                                    'signal': <django.dispatch.dispatcher.Signalobjectat0x7f44749958d0>,
                                    'using': 'default'
                                }
    """

    # import model inside function to avoid circular dependency
    from device.models import DeviceType
    from site_instance.models import SiteInstance

    # instance before saving the form
    old_instance = None
    try:
        old_instance = DeviceType.objects.get(id=instance.id)
    except Exception as e:
        pass

    if old_instance:
        # old fields values list
        old_values = [old_instance.rta_critical,
                      old_instance.rta_warning,
                      old_instance.pl_critical,
                      old_instance.pl_warning]
        old_values = [x for x in old_values if x is not None]

        # new fields values list
        new_values = [instance.rta_critical,
                      instance.rta_warning,
                      instance.pl_critical,
                      instance.pl_warning]
        new_values = [x for x in new_values if x is not None]

        if (len(new_values) != len(old_values)) or (list(set(old_values) - set(new_values))):
            # modify all site instances 'is_device_change' bit to 1
            SiteInstance.objects.all().update(is_device_change=1)


def update_site_on_service_change(sender, instance=None, created=False, **kwargs):
    """
        Set 'is_device_change' for all site instances to 1 if service is modified in device type
        Parameters:
            - sender (<class 'django.db.models.base.ModelBase'>) - sender model class
                                                                   i.e. <class 'device.models.DeviceTypeService'>
            - instance (<class 'device.models.DeviceTypeService'>) - instance being saved
                                                                     for e.g. DeviceTypeService object
            - created (bool) - object created or updated
            - kwargs (dict) - a dictionary of keyword arguments passed to constructor for e.g.
                                {
                                    'update_fields': None,
                                    'raw': False,
                                    'signal': <django.dispatch.dispatcher.Signalobjectat0x7f44749958d0>,
                                    'using': 'default'
                                }
    """

    # import model inside function to avoid circular dependency
    from site_instance.models import SiteInstance

    # modify all site instances 'is_device_change' bit to 1
    SiteInstance.objects.all().update(is_device_change=1)


def update_device_type_service(sender, instance=None, created=False, **kwargs):
    """
    If a new device type service is created auto assign default data source of service to it.
    """
    if not created:
        return

    DeviceTypeServiceDataSource = get_model('device', 'DeviceTypeServiceDataSource', seed_cache=True)
    ServiceSpecificDataSource = get_model('service', 'ServiceSpecificDataSource', seed_cache=True)

    dt_sds = list()
    service_ds = ServiceSpecificDataSource.objects.filter(service=instance.service)
    for ds in service_ds:
        kwargs=dict(device_type_service=instance,
                    service_data_sources=ds.service_data_sources,
                    warning=ds.warning,
                    critical=ds.critical)
        dt_sds.append(DeviceTypeServiceDataSource(**kwargs))

    DeviceTypeServiceDataSource.objects.bulk_create(dt_sds)