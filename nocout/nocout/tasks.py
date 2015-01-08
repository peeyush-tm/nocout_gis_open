"""
Provide celery tasks for project.
"""

from celery import task
from django.core.cache import cache

from celery.utils.log import get_task_logger
logger = get_task_logger(__name__)


@task()
def cache_clear_task():
    """
    Celery task to clean complete cache.
    """
    try:
        cache.clear()
        cache._cache.flush_all()
    except Exception as e:
        logger.exception(e.message)
