from django.db.models import Q
from nocout.utils.util import disable_for_loaddata


@disable_for_loaddata
def assign_default_thematics_to_user(sender, instance=None, created=False, **kwargs):
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

    if created:
        # import model inside function to avoid circular dependency
        from inventory.models import (ThematicSettings,
                                      UserThematicSettings,
                                      PingThematicSettings,
                                      UserPingThematicSettings)
        from device.models import DeviceTechnology

        # user profile
        user_profile = instance

        # get thematics for ptp
        tech_ptp = None
        tech_pmp = None
        tech_wimax = None
        try:
            tech_ptp = DeviceTechnology.objects.get(id=2)
            tech_pmp = DeviceTechnology.objects.get(id=4)
            tech_wimax = DeviceTechnology.objects.get(id=3)
        except Exception as e:
            pass

        # ********************* ASSIGN THEMATIC SETTINGS ***********************

        # # get global thematic settings for p2p, pmp, wimax
        # thematics_ptp = ThematicSettings.objects.filter(name__icontains="RSSI", is_global=True).filter(
        #     name__icontains="ptp")
        #
        # thematics_pmp = ThematicSettings.objects.filter(name__icontains="RSSI", is_global=True).filter(
        #     name__icontains="DL").filter(name__icontains="pmp")
        #
        # thematics_wimax = ThematicSettings.objects.filter(name__icontains="RSSI", is_global=True).filter(
        #     name__icontains="DL").filter(name__icontains="wimax")
        #
        # # assign user thematics for ptp, pmp, wimax
        # for tech in ['ptp', 'pmp', 'wimax']:
        #     if eval("thematics_{}".format(tech)):
        #         UserThematicSettings.objects.create(
        #             user_profile=user_profile,
        #             thematic_template=eval("thematics_{}[0]".format(tech)),
        #             thematic_technology=eval("tech_{}".format(tech))
        #         )

        # ********************* ASSIGN PING THEMATIC SETTINGS ***********************

        # get ping thematic settings for p2p, pmp, wimax
        ping_thematics_ptp = PingThematicSettings.objects.filter(Q(is_global=True), Q(name__icontains="ptp"), Q(
            name__icontains="PL") | Q(name__icontains="Packet"))

        ping_thematics_pmp = PingThematicSettings.objects.filter(Q(is_global=True), Q(name__icontains="pmp"), Q(
            name__icontains="PL") | Q(name__icontains="Packet"))

        ping_thematics_wimax = PingThematicSettings.objects.filter(Q(is_global=True), Q(name__icontains="wimax"), Q(
            name__icontains="PL") | Q(name__icontains="Packet"))

        # assign user ping thematics for ptp, pmp, wimax
        for tech in ['ptp', 'pmp', 'wimax']:
            if eval("ping_thematics_{}".format(tech)):
                UserPingThematicSettings.objects.create(
                    user_profile=user_profile,
                    thematic_template=eval("ping_thematics_{}[0]".format(tech)),
                    thematic_technology=eval("tech_{}".format(tech))
                )
