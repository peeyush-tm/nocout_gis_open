from django.db import models
import time
from datetime import datetime
from user_profile.models import UserProfile
from django.contrib.auth.models import User


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

#************************** KMZ Model *******************************#
class KMZReport(models.Model):

	#Function for modify path of upload file #
	def KMZ_report_name(instance, filename):

		timestamp = time.time()
		full_time = datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d-%H-%M-%S')
		year_month_date = datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d')

		# modified filename
		filename = "{}_{}".format(full_time, filename)

		# modified path where file is uploaded
		path = "uploaded/KMZ"

		return '{}/{}/{}'.format(path, year_month_date, filename)

	name = models.CharField('Name', max_length=255, unique=True)
	filename = models.FileField(max_length=300, upload_to=KMZ_report_name)
	added_on = models.DateTimeField('Added On',blank=True, auto_now_add=True)
	user = models.ForeignKey(UserProfile)
	is_public = models.BooleanField('Is Public', default=True)

	

	

