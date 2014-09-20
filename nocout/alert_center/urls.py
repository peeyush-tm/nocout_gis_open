from django.conf.urls import patterns, url
from alert_center import views


urlpatterns = patterns('',
    url(r'^network/(?P<data_source>\w+)/$', views.AlertCenterNetworkListing.as_view()),

    url(r'^networklistingtable/',views.AlertCenterNetworkListingTable.as_view(), name='NetworkAlertListingTable'),

    # url(r'^latencylistingtable/',views.AlertCenterNetworkListingTable.as_view(), name='LatencyListingTable'),
    #
    # url(r'^packetdroplistingtable/',views.AlertCenterNetworkListingTable.as_view(), name='PacketDropListingTable'),
    #
    # url(r'^downlistingtable/',views.AlertCenterNetworkListingTable.as_view(), name='DownListingTable'),
    #
    # url(r'^servicealertslistingtable/',views.AlertCenterNetworkListingTable.as_view(), name='ServiceAlertListingTable'),

    url(r'^customer/(?P<data_source>\w+)/$', views.CustomerAlertList.as_view()),

    url(r'^customerlistingtable/',views.CustomerAlertListingTable.as_view(), name='CustomerAlertListingTable'),

    # url(r'^customer/packet_drop/$', views.CustomerPacketDropList.as_view()),
    url(r'^detail/customer_detail/$', views.getCustomerAlertDetail),

    url(r'^detail/customer_detail_listing_table/', views.GetCustomerAlertDetail.as_view(), name='Customer_PTP_Block_Table'),

    url(r'^detail/network_detail/$', views.getNetworkAlertDetail),

    url(r'^detail/network_detail_listing_table$', views.GetNetworkAlertDetail.as_view(), name='Network_PTP_Block_Table'),

    url(r'^(?P<page_type>\w+)/device/(?P<device_id>\w+)/service_tab/(?P<service_name>\w+)/$',
        views.SingleDeviceAlertDetails.as_view(),
        name='SingleDeviceDetails'
    ),

    url(r'^detail/network_detail/$', views.getNetworkAlertDetail),




)