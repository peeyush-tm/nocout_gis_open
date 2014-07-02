from django.conf.urls import patterns, url
from alert_center import views


urlpatterns = patterns('',
    url(r'^network/$', views.LatencyList.as_view()),
    url(r'^customer/(?P<page_type>\w+)/$', views.CustomerLatencyList.as_view()),
    url(r'^detail/customer_detail/$', views.getCustomerAlertDetail),
    url(r'^detail/network_detail/$', views.getNetworkAlertDetail),
    url(r'^latencylist/',views.LatencyList.as_view(), name='LatencyList'),
    url(r'^latencylistingtable/',views.LatencyListingTable.as_view(), name='LatencyListingTable'),
    url(r'^packetdroplistingtable/',views.PacketDropListingTable.as_view(), name='PacketDropListingTable'),
    url(r'^downlistingtable/',views.DownListingTable.as_view(), name='DownListingTable'),
    url(r'^servicealertslistingtable/',views.ServiceAlertsListingTable.as_view(), name='ServiceAlertsListingTable'),
)