"""
Module which defines signals.
"""

from django.db.models.signals import post_save
from django.dispatch import receiver
from user_profile.models import UserProfile
from inventory.models import ThematicSettings, UserThematicSettings



@receiver(post_save, sender=UserProfile)
def auto_assign_thematic(sender, **kwargs):
	try:
		thematicSetting = ThematicSettings.objects.filter(name__contains='RSSI')[0]
		m=UserThematicSettings(thematic_template=thematicSetting, user_profile=kwargs.get('instance'))
		m.save()
	except:
		pass