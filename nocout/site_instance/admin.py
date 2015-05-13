"""
====================================================
Module used to register models with admin interface.
====================================================

Location:
* /nocout_gis/nocout/site_instance/admin.py
"""

from django.contrib import admin
from site_instance.models import SiteInstance

admin.site.register(SiteInstance)
