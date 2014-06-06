
from django.conf.urls import patterns, include, url
from .views import dialog_action


urlpatterns = patterns('',
                       url(r'^dialog_action/$', dialog_action)

                       )