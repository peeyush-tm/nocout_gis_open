"""
===========================================================================================
Module contains url configuration specific to 'device sync history' module in 'device' app.
===========================================================================================

Location:
* /nocout_gis/nocout/device/device_sync_history_urls.py
"""

from django.conf.urls import patterns, url
import views

urlpatterns = patterns('',
                       url(r'^$', views.DeviceSyncHistoryList.as_view(), name='device_sync_history_list'),
                       url(r'^devicesynchistorylistingtable/', views.DeviceSyncHistoryListingTable.as_view(),
                           name='DeviceSyncHistoryListingTable'),
                       url(r'^(?P<pk>\d+)/delete/$', views.DeviceSyncHistoryDelete.as_view(),
                           name='device_sync_history_delete'),
                       url(r'^(?P<pk>\d+)/edit/$', views.DeviceSyncHistoryUpdate.as_view(),
                           name='device_sync_history_edit'),
                       )