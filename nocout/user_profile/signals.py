"""
Module which defines signals.
"""

from django.db.models.signals import post_save, pre_delete
from django.dispatch import receiver
from user_profile.models import UserProfile
from inventory.models import ThematicSettings, UserThematicSettings
from activity_stream.models import UserAction

@receiver(post_save, sender=UserProfile)
def auto_assign_thematic(sender, instance=None, created=False, **kwargs):
    """
    If a new user is created auto assign rssi thematic settings for P2P, PMP and WiMAX technologies.
    """

    if not created:
        return

    # Technology P2P
    thematic_setting_p2p = ThematicSettings.objects.filter(
            threshold_template__live_polling_template__technology__name='P2P',
            name__icontains="RSSI",
    )[:1]

    if len(thematic_setting_p2p)>0:
        UserThematicSettings.objects.create(
                thematic_template=thematic_setting_p2p[0],
                thematic_technology=thematic_setting_p2p[0].threshold_template.live_polling_template.technology,
                user_profile=instance,
        )

    # Technology PMP
    thematic_setting_pmp = ThematicSettings.objects.filter(
            threshold_template__live_polling_template__technology__name='PMP',
            name__icontains="RSSI",
    )[:1]

    if len(thematic_setting_pmp)>0:
        UserThematicSettings.objects.create(
                thematic_template=thematic_setting_pmp[0],
                thematic_technology=thematic_setting_pmp[0].threshold_template.live_polling_template.technology,
                user_profile=instance,
        )

    # Technology WiMAX
    thematic_setting_wimax = ThematicSettings.objects.filter(
            threshold_template__live_polling_template__technology__name='WIMAX',
            name__icontains="RSSI",
    )[:1]

    if len(thematic_setting_wimax)>0:
        UserThematicSettings.objects.create(
                thematic_template=thematic_setting_wimax[0],
                thematic_technology=thematic_setting_wimax[0].threshold_template.live_polling_template.technology,
                user_profile=instance,
        )

@receiver(pre_delete, sender=UserProfile)
def delete_user_related_log(sender, instance, using, **kwargs):
    user_log = UserAction.objects.filter(user_id=instance.id)
    user_log.delete()
