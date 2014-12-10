from django.conf.urls import patterns, url
from scheduling_management import views


urlpatterns = patterns('',
    url(r'^$', views.get_scheduler, name='scheduler'),
    url(r'^new/$', views.EventCreate.as_view(), name='event_new'),
)
