from django.conf.urls import patterns, url
from performance import views

urlpatterns = patterns('',
	url(r'^(?P<page_type>\w+)_live/$', views.get_live_performance),
	url(r'^(?P<page_type>\w+)_live/(?P<device_id>\w+)/$', views.get_performance),
	url(r'^performance_dashboard/$', views.get_performance_dashboard),
	url(r'^sector_dashboard/$', views.get_sector_dashboard)
)