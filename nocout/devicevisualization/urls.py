from django.conf import settings
from django.conf.urls import patterns, url, include
from devicevisualization import views

from django.views.decorators.cache import cache_page
#in case same base station is called twice in less than
#3 minutes

urlpatterns = patterns('',
                       url(r'^maps/(?P<page_type>\w+)/$', views.init_network_maps, name='init_network_maps'),
                       url(r'^kmz/$', views.KmzListing.as_view(), name='kmz_list'),
                       url(r'^kmz/(?P<kmz_id>\d+)/(?P<page_type>\w+)/view/$', views.KmzViewAction.as_view(),
                           name='kmz_view_action'),
                       url(r'^kmzListing/$', views.Kmzreport_listingtable.as_view(), name='Kmzreport_listingtable'),
                       url(r'^kmz/add/$', views.KmzCreate.as_view(), name='kmz_upload'),
                       url(r'^kmz/delete/(?P<kmz_id>\d+)/$', views.KmzDelete.as_view(), name='kmz_delete'),
                       url(r'^gis/(?P<device_name>\w+)/$', views.init_network_maps, name='init_maps_for_single_device'),
                       url(r'^points/$', views.PointListingInit.as_view(), name='point_listing'),
                       url(r'^pointsListing/$', views.PointListingTable.as_view(), name='point_listing_table'),
                       url(r'^performance_data/$', views.Gis_Map_Performance_Data.as_view(),
                           name='gis_map_performance_data'),
                       url(r'^tools/point/$', views.PointToolClass.as_view(), name='point_tool_class'),
                       url(r'^get_tools_data/$', views.GetToolsData.as_view(), name='get_tools_data'),
                       #in case the base station call returns before 3 minutes
                       #send out the cached response
                       url(r'^perf_data/$',
                           cache_page(60 * 3)(views.GISPerfData.as_view()),
                           name='gis_perf_data'),
                       url(r'^static_info/$',
                           cache_page(60 * 3)(views.GISStaticInfo.as_view()),
                           name='gis_static_info'),
                       url(r'^perf_info/$',
                           cache_page(60 * 3)(views.GISPerfInfo.as_view()),
                           name='gis_perf_info'),

                       url(r'^l2_report/(?P<item_id>\w+)/(?P<type>\w+)/$', views.getL2Report, name='get_l2_report'),
                       url(r'^update_maintenance_status/$', views.UpdateMaintenanceStatus.as_view(),
                           name='update_maintenance_status'),
               )
