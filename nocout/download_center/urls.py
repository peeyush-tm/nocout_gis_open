from django.conf.urls import patterns, url
from download_center import views

urlpatterns = patterns('',
    url(
        r'^inventory/(?P<page_type>\w+)/$',
        views.DownloadCenter.as_view(),
        name='InventoryDownloadCenter'
    ),
    # url(
    #     r'^network/(?P<page_type>\w+)/$',
    #     views.BSOutageReportList.as_view(),
    #     name='BSOutageReport'
    # ),
    # url(
    #     r'^network/(?P<page_type>\w+)/listig/$',
    #     views.DownloadCenterListing.as_view(),
    #     name='bs_outage_report_listing'
    # ),
    url(
        r'^downloadcenterlistingtable/$',
        views.DownloadCenterListing.as_view(),
        name='DownloadCenterListing'
    ),
    url(
        r'^delete/(?P<pk>\d+)$',
        views.DownloadCenterReportDelete.as_view(),
        name='report_delete'
    ),
    url(
        r'^citycharter/headers/$',
        views.CityCharterReportHeaders.as_view(),
        name='CityCharterReportHeaders'
    ),
    url(
      r'^citycharter/listing/(?P<is_data_limited>\w+)/$',
      views.CityCharterReportListing.as_view(),
      name='CityCharterReportListing'
    )
)
