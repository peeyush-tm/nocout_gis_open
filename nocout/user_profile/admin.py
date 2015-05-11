"""
====================================================
Module used to register models with admin interface.
====================================================

Location:
* /nocout_gis/nocout/user_profile/admin.py
"""

from django.contrib import admin
from .models import UserProfile


# Registering 'UserProfile' model with the admin interface.
admin.site.register(UserProfile)
