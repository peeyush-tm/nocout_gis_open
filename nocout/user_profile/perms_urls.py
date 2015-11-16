"""
=========================================================
Module contains url configuration for 'permission' app.
=========================================================

Location:
* /nocout_gis/nocout/user_profile/permission_urls.py
"""

from django.conf.urls import patterns, url
from user_profile import views

urlpatterns = patterns('',
                       url(r'^$', views.PermissionList.as_view(), name='permissions_list'),
                       url(r'^(?P<pk>\d+)/$', views.PermissionDetail.as_view(), name='permission_detail'),
                       url(r'^new/$', views.PermissionCreate.as_view(), name='permission_new'),
                       url(r'^(?P<pk>\d+)/edit/$', views.PermissionUpdate.as_view(), name='permission_edit'),
                       url(r'^(?P<pk>\d+)/delete/$', views.PermissionDelete.as_view(), name='permission_delete'),
                       url(r'^permissionlistingtable/', views.PermissionListingTable.as_view(), name='PermissionListingTable'))
