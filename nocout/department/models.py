# Create your models here.
from django.db import models
from user_group.models import UserGroup
from user_profile.models import UserProfile
class Department(models.Model):
	User_group =models.ForeignKey(UserGroup)
	User_profile =models.ForeignKey(UserProfile)
	




