from django.conf.urls import patterns, url
from performance import views
from performance.views import Get_Service_Type_Performance_Data

urlpatterns = patterns('',
	url(r'^(?P<page_type>\w+)_live/$', views.get_live_performance),
	url(r'^(?P<page_type>\w+)_live/(?P<device_id>\w+)/$', views.get_performance),
	url(r'^performance_dashboard/$', views.get_performance_dashboard),
	url(r'^sector_dashboard/$', views.get_sector_dashboard),
	url(r'^get_substation_devices/$', views.get_substation_devices),
	url(r'^get_substation_status/(?P<device_id>\d+)/$', views.get_substation_status),
	url(r'^get_substation_services/(?P<device_id>\d+)/$', views.get_substation_services),
	# url(r'^service/(?P<service_type>\w+)/data/(?P<device_id>\d+)$', views.get_service_type_performance_data),
	url(r'^service/(?P<service_type>\w+)/data/(?P<device_id>\d+)$', Get_Service_Type_Performance_Data.as_view())
)