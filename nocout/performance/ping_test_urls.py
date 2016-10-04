from django.conf.urls import patterns, url
from performance import views

urlpatterns = patterns('',
	url(r'^$', views.InitStabilityTest.as_view(), name='ping_stability_test'),
	url(r'^listing/$', views.PingStabilityTestListing.as_view(), name='ping_test_listing'),
)
