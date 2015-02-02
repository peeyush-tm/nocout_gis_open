"""
Provide celery tasks for project.
"""

from celery import task
from django.core.cache import cache

@task()
def cache_clear_task():
    """
    Celery task to clean complete cache.
    """
    try:
        cache.clear()
        cache._cache.flush_all()
    except:
        pass
