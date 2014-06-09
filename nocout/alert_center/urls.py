from django.conf.urls import patterns, url
from alert_center import views


urlpatterns = patterns('',
    url(r'^network/$', views.getNetworkAlert),
    url(r'^customer/(?P<page_type>\w+)/$', views.getCustomerAlert),
    url(r'^detail/customer_detail/$', views.getCustomerAlertDetail),
    url(r'^detail/network_detail/$', views.getNetworkAlertDetail)
)