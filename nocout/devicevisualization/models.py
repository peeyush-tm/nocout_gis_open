from django.db import models

#************************** Google maps tools model **************************#

# Model for point tools
class GISPointTool(models.Model):
	
	name = models.CharField('Name', max_length=200, unique=True)
	description = models.TextField('Description', null=True, blank=True)
	latitude = models.FloatField('Latitude', null=True, blank=True)
	longitude = models.FloatField('Longitude', null=True, blank=True)
	icon_url = models.CharField('Icon Url', max_length=255, unique=False)
	connected_point_type = models.CharField('Connected Point Type', max_length=255, null=True, blank=True)
	connected_point_info = models.TextField('Connected Point Info', null=True, blank=True)
	connected_lat = models.FloatField('Connected Latitude', null=True, blank=True)
	connected_lon = models.FloatField('Connected Longitude', null=True, blank=True)
	user_id = models.IntegerField('User Id')

	def __unicode__(self):
	    return self.name