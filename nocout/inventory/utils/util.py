# -*- coding: utf-8 -*-

#python core functions
import datetime

#django settings
from django.conf import settings

#django core model functions
from django.db.models import Count, Q

#nocout specific functions
from device.models import Device

#nocout utilities
from nocout.utils.util import *

#logging the performance of function
import logging
log = logging.getLogger(__name__)
#logging the performance of function


