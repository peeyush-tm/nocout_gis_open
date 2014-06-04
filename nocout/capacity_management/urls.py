from django.conf.urls import patterns, url
from capacity_management import views


urlpatterns = patterns('',
    url(r'^daily_alert/(?P<alert_type>\w+)/$', views.get_daily_alerts),
    url(r'^status/(?P<status_type>\w+)/$', views.get_utilization_status),
)