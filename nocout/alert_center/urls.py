from django.conf.urls import patterns, url
from alert_center import views


urlpatterns = patterns('',
    url(r'^network/$', views.AlertCenterNetworkListing.as_view()),
    url(r'^latencylistingtable/',views.AlertCenterNetworkListingTable.as_view(), name='LatencyListingTable'),
    url(r'^packetdroplistingtable/',views.AlertCenterNetworkListingTable.as_view(), name='PacketDropListingTable'),
    url(r'^customer/(?P<data_source>\w+)/$', views.CustomerAlertList.as_view()),
    url(r'^customerlistingtable/',views.CustomerAlertListingTable.as_view(), name='CustomerAlertListingTable'),
    # url(r'^customer/packet_drop/$', views.CustomerPacketDropList.as_view()),
    url(r'^detail/customer_detail/$', views.getCustomerAlertDetail),
    url(r'^detail/network_detail/$', views.getNetworkAlertDetail),
    # url(r'^latencylist/',views.AlertCenterNetworkListing.as_view(), name='AlertCenterNetworkListing'),
    # url(r'^downlistingtable/',views.DownListingTable.as_view(), name='DownListingTable'),
    # url(r'^servicealertslistingtable/',views.ServiceAlertsListingTable.as_view(), name='ServiceAlertsListingTable'),
)