"""
Module which defines signals.
"""

from django.db.models.signals import post_save
from django.dispatch import receiver
from user_profile.models import UserProfile
from inventory.models import ThematicSettings, UserThematicSettings


@receiver(post_save, sender=UserProfile)
def auto_assign_thematic(sender, **kwargs):
    thematic_setting_p2p=ThematicSettings.objects.filter(threshold_template__live_polling_template__technology__name='P2P', name__contains="RSSI")[:1]
    if len(thematic_setting_p2p)>0:
        UserThematicSettings.objects.create(thematic_template=thematic_setting_p2p[0], thematic_technology=thematic_setting_p2p[0].threshold_template.live_polling_template.technology, user_profile=kwargs.get('instance'))

    thematic_setting_pmp=ThematicSettings.objects.filter(threshold_template__live_polling_template__technology__name='PMP', name__contains="RSSI")[:1]
    if len(thematic_setting_pmp)>0:
        UserThematicSettings.objects.create(thematic_template=thematic_setting_pmp[0],thematic_technology=thematic_setting_pmp[0].threshold_template.live_polling_template.technology, user_profile=kwargs.get('instance'))

    thematic_setting_wimax=ThematicSettings.objects.filter(threshold_template__live_polling_template__technology__name='WIMAX',name__contains="RSSI")[:1]
    if len(thematic_setting_wimax)>0:
        UserThematicSettings.objects.create(thematic_template=thematic_setting_wimax[0],thematic_technology=thematic_setting_wimax[0].threshold_template.live_polling_template.technology, user_profile=kwargs.get('instance'))
