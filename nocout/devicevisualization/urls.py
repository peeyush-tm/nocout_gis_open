from django.conf import settings
from django.conf.urls import patterns, url, include
from devicevisualization import views


urlpatterns = patterns('',
                       url(r'^$', views.locate_devices),
                       url(r'^gis/$', views.locate_devices),
                       url(r'^google_earth/$', views.load_google_earth),
                       url(r'^googleEarth/$', views.load_earth),
                       url(r'^white_background/$', views.load_white_background),
                       url(r'^kmz/$', views.KmzListing.as_view(), name='kmz_list'),
                       url(r'^kmz/(?P<kmz_id>\d+)/(?P<page_type>\w+)/view/$', views.KmzViewAction.as_view(),
                           name='kmz_view_action'),
                       url(r'^kmzListing/$', views.Kmzreport_listingtable.as_view(), name='Kmzreport_listingtable'),
                       url(r'^kmz/add/$', views.KmzCreate.as_view(), name='kmz_upload'),
                       url(r'^kmz/delete/(?P<kmz_id>\d+)/$', views.KmzDelete.as_view(), name='kmz_delete'),
                       url(r'^gis/(?P<device_name>\w+)/$', views.locate_devices),
                       url(r'^points/$', views.PointListingInit.as_view(), name='point_listing'),
                       url(r'^pointsListing/$', views.PointListingTable.as_view(), name='point_listing_table'),
                       url(r'^performance_data/$', views.Gis_Map_Performance_Data.as_view(),
                           name='gis_map_performance_data'),
                       url(r'^download_selected_bs_inventory/$', views.DownloadSelectedBSInventory.as_view(),
                           name='download_selected_bs_inventory'),
                       url(r'^tools/point/$', views.PointToolClass.as_view(), name='point_tool_class'),
                       url(r'^get_tools_data/$', views.GetToolsData.as_view(), name='get_tools_data'),
                       url(r'^perf_data/$', views.GISPerfData.as_view(), name='gis_perf_data'))
