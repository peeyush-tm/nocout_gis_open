from django.core.cache import cache
from django.core.management.base import BaseCommand

class Command(BaseCommand):
    def handle(self, *args, **options):
        try:
            cache.clear()
            cache._cache.flush_all()
        except:
            pass