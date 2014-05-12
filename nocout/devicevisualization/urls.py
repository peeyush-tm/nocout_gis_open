from django.conf import settings
from django.conf.urls import patterns, url, include
from devicevisualization import views

urlpatterns = patterns('',
	url(r'^$', views.locate_devices),		
)
