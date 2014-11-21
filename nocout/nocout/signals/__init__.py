"""
Define signal to clear cache.
"""
from django.db.models.signals import class_prepared, post_save, post_delete
from django.conf import settings

from nocout.tasks import cache_clear_task


def clear_cache(sender, **kwargs):
    """
    Call celery job to clear complete cache.
    """
    cache_clear_task()


def register_cache_clear_signal(sender, **kwargs):
    """
    Register app models to allow clearing cache on post_save and post_delete signals.
    """

    if sender._meta.app_label in settings.ALLOWED_APPS_TO_CLEAR_CACHE:
        post_save.connect(clear_cache, sender=sender)
        post_delete.connect(clear_cache, sender=sender)


class_prepared.connect(register_cache_clear_signal)
