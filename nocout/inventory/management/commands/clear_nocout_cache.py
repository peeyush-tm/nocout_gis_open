from django.core.cache import cache
from django.core.management.base import BaseCommand
from machine.models import Machine
from django.db import connections

import logging
logger = logging.getLogger(__name__)

class Command(BaseCommand):
    def handle(self, *args, **options):
        try:
            #nocout cache clear
            cache.clear()
            # cache._cache.flush_all()
            #nocout cache clear
            #mysql cache clear
            query = "RESET QUERY CACHE; "
            query += "FLUSH QUERY CACHE; "
            #mysql cache clear
            machines = Machine.objects.filter().values_list('name',flat=True)
            for machine in machines:
                cursor = connections[machine].cursor()
                cursor.execute(query)
            #mysql cache clear #only for primary machines
            #to do check for subordinates reset as well? or would it happen automatically ?
        except Exception as e:
            logger.exception(e.message)