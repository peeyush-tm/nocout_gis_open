"""
    Signals associated with service app.
"""


def update_site_on_protocol_change(sender, instance=None, created=False, **kwargs):
    """
        Set 'is_device_change' for all site instances to 1 if protocol is modified
        Parameters:
            - sender (<class 'django.db.models.base.ModelBase'>) - sender model class
                                                                   i.e. <class 'service.models.Protocol'>
            - instance (<class 'service.models.Protocol'>) - instance being saved
                                                                     for e.g. Protocol object
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


def update_site_on_ds_change(sender, instance=None, created=False, **kwargs):
    """
        Set 'is_device_change' in site instance to 1 if data source created or modified
        Parameters:
            - sender (<class 'mptt.models.MPTTModelBase'>) - sender model class
                                                             i.e. <class 'service.models.ServiceDataSource'>
            - instance (<class 'service.models.ServiceDataSource'>) - instance being saved for e.g. Default
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
    from service.models import ServiceDataSource
    from site_instance.models import SiteInstance

    # instance before saving the form
    old_instance = None
    try:
        old_instance = ServiceDataSource.objects.get(id=instance.id)
    except Exception as e:
        pass

    if old_instance:
        # old fields values list
        old_values = [old_instance.warning,
                      old_instance.critical]
        old_values = [x for x in old_values if x is not None]

        # new fields values list
        new_values = [instance.warning,
                      instance.critical]
        new_values = [x for x in new_values if x is not None]

        if (len(new_values) != len(old_values)) or (list(set(old_values) - set(new_values))):
            # modify all site instances 'is_device_change' bit to 1
            SiteInstance.objects.all().update(is_device_change=1)


def update_site_on_service_change(sender, instance=None, created=False, **kwargs):
    """
        Set 'is_device_change' in site instance to 1 if service name in service is created or modified
        Parameters:
            - sender (<class 'mptt.models.MPTTModelBase'>) - sender model class i.e. <class 'service.models.Service'>
            - instance (<class 'service.models.Service'>) - instance being saved for e.g. Default
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
    from service.models import Service
    from site_instance.models import SiteInstance

    # instance before saving the form
    old_instance = None
    try:
        old_instance = Service.objects.get(id=instance.id)
    except Exception as e:
        pass

    if old_instance:
        # old fields values list
        old_values = [old_instance.name]
        old_values = [x for x in old_values if x is not None]

        # new fields values list
        new_values = [instance.name]
        new_values = [x for x in new_values if x is not None]

        if (len(new_values) != len(old_values)) or (list(set(old_values) - set(new_values))):
            # modify all site instances 'is_device_change' bit to 1
            SiteInstance.objects.all().update(is_device_change=1)


def update_site_on_svc_specific_ds_change(sender, instance=None, created=False, **kwargs):
    """
        Set 'is_device_change' for all site instances to 1 if service specific data source is modified in device type
        Parameters:
            - sender (<class 'django.db.models.base.ModelBase'>) - sender model class
                                                                i.e. <class 'service.models.ServiceSpecificDataSource'>
            - instance (<class 'service.models.ServiceSpecificDataSource'>) - instance being saved
                                                                     for e.g. ServiceSpecificDataSource object
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


def update_site_on_svcconf_change(sender, instance=None, created=False, **kwargs):
    """
        Set 'is_device_change' for all site instances to 1 if service configuration is modified
        Parameters:
            - sender (<class 'django.db.models.base.ModelBase'>) - sender model class
                                                                i.e. <class 'service.models.DeviceServiceConfiguration'>
            - instance (<class 'service.models.DeviceServiceConfiguration'>) - instance being saved
                                                                           for e.g. DeviceServiceConfiguration object
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


def update_site_on_pingconf_change(sender, instance=None, created=False, **kwargs):
    """
        Set 'is_device_change' in site instance to 1 if ping configuration is created or modified
        Parameters:
            - sender (<class 'mptt.models.MPTTModelBase'>) - sender model class
                                                             i.e. <class 'service.models.DevicePingConfiguration'>
            - instance (<class 'service.models.DevicePingConfiguration'>) - instance being saved for e.g. Default
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
    from service.models import DevicePingConfiguration
    from site_instance.models import SiteInstance

    # instance before saving the form
    old_instance = None
    try:
        old_instance = DevicePingConfiguration.objects.get(id=instance.id)
    except Exception as e:
        pass

    if old_instance:
        # old fields values list
        old_values = [old_instance.device_name,
                      old_instance.rta_critical,
                      old_instance.rta_warning,
                      old_instance.pl_critical,
                      old_instance.pl_warning]
        old_values = [x for x in old_values if x is not None]

        # new fields values list
        new_values = [instance.device_name,
                      instance.rta_critical,
                      instance.rta_warning,
                      instance.pl_critical,
                      instance.pl_warning]
        new_values = [x for x in new_values if x is not None]

        if (len(new_values) != len(old_values)) or (list(set(old_values) - set(new_values))):
            # modify all site instances 'is_device_change' bit to 1
            SiteInstance.objects.all().update(is_device_change=1)
