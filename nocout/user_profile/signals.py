"""
=======================================================
Module contains signals specific to 'user_profile' app.
=======================================================

Location:
* /nocout_gis/nocout/user_profile/signals.py

List of constructs:
=======
Functions
=======
* assign_default_thematics_to_user
"""

from django.db.models import Q
# Import nocout utils gateway class
from nocout.utils.util import NocoutUtilsGateway

# Create instance of 'NocoutUtilsGateway' class
nocout_utils = NocoutUtilsGateway()


@nocout_utils.disable_for_loaddata
def assign_default_thematics_to_user(sender, instance=None, created=False, **kwargs):
    """
        Assigning default thematics to user on it's creation.
        Args:
            sender (<class 'mptt.models.MPTTModelBase'>): Sender model class, i.e. <class 'device.models.Device'>.
            instance (<class 'device.models.Device'>): Instance being saved. For e.g. Default.
            created (bool): Object created or updated.
            **kwargs: Arbitrary keyword arguments. Dictionary of keyword arguments passed to constructor.
                      For e.g.
                            {
                                'update_fields': None,
                                'raw': False,
                                'signal': <django.dispatch.dispatcher.Signalobjectat0x7f44749958d0>,
                                'using': 'default'
                            }
    """
    if created:
        # Import model inside function to avoid circular dependency.
        from inventory.models import (ThematicSettings,
                                      UserThematicSettings,
                                      PingThematicSettings,
                                      UserPingThematicSettings)
        from device.models import DeviceTechnology

        user_profile = instance

        # Get thematics for PTP.
        tech_ptp = None
        tech_pmp = None
        tech_wimax = None
        try:
            tech_ptp = DeviceTechnology.objects.get(id=2)
            tech_pmp = DeviceTechnology.objects.get(id=4)
            tech_wimax = DeviceTechnology.objects.get(id=3)
        except Exception as e:
            pass

        # *********************** ASSIGN THEMATIC SETTINGS *************************

        # # Get global thematic settings for PTP, PMP, WiMAX.
        # thematics_ptp = ThematicSettings.objects.filter(name__icontains="RSSI", is_global=True).filter(
        #     name__icontains="ptp")
        #
        # thematics_pmp = ThematicSettings.objects.filter(name__icontains="RSSI", is_global=True).filter(
        #     name__icontains="DL").filter(name__icontains="pmp")
        #
        # thematics_wimax = ThematicSettings.objects.filter(name__icontains="RSSI", is_global=True).filter(
        #     name__icontains="DL").filter(name__icontains="wimax")
        #
        # # Assign user thematics for PTP, PMP, WiMAX.
        # for tech in ['ptp', 'pmp', 'wimax']:
        #     if eval("thematics_{}".format(tech)):
        #         UserThematicSettings.objects.create(
        #             user_profile=user_profile,
        #             thematic_template=eval("thematics_{}[0]".format(tech)),
        #             thematic_technology=eval("tech_{}".format(tech))
        #         )

        # ********************* ASSIGN PING THEMATIC SETTINGS ***********************

        # Get ping thematic settings for PTP, PMP, WiMAX.
        ping_thematics_ptp = PingThematicSettings.objects.filter(
            Q(is_global=True),
            Q(technology__name__iexact="P2P"),
            (Q(data_source__icontains="pl") | Q(name__icontains="Packet"))
        )

        ping_thematics_pmp = PingThematicSettings.objects.filter(
            Q(is_global=True),
            Q(technology__name__iexact="PMP"),
            (Q(data_source__icontains="pl") | Q(name__icontains="Packet"))
        )

        ping_thematics_wimax = PingThematicSettings.objects.filter(
            Q(is_global=True),
            Q(technology__name__iexact="WiMAX"),
            (Q(data_source__icontains="pl") | Q(name__icontains="Packet"))
        )

        # Assign user ping thematics for PTP, PMP, WiMAX.
        for tech in ['ptp', 'pmp', 'wimax']:
            if eval("ping_thematics_{}".format(tech)):
                for thematic in eval("ping_thematics_{}".format(tech)):
                    UserPingThematicSettings.objects.create(
                        user_profile=user_profile,
                        thematic_template=thematic,
                        thematic_technology=thematic.technology,
                        thematic_type=thematic.type
                    )