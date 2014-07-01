from django.conf import settings
from django.conf.urls import patterns, url, include
from devicevisualization import views

urlpatterns = patterns('',
    url(r'^$', views.locate_devices),
	url(r'^gis/$', views.locate_devices),
	url(r'^gis/(?P<device_name>\w+)/$', views.locate_devices),
)
