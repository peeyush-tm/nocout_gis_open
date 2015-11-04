"""
=========================================================
Module contains url configuration for 'group' app.
=========================================================

Location:
* /nocout_gis/nocout/user_profile/group_urls.py
"""

from django.conf.urls import patterns, url
from user_profile import views

urlpatterns = patterns('',
                       url(r'^$', views.GroupList.as_view(), name='groups_list'),
                       url(r'^(?P<pk>\d+)/$', views.GroupDetail.as_view(), name='group_detail'),
                       url(r'^new/$', views.GroupCreate.as_view(), name='group_new'),
                       url(r'^(?P<pk>\d+)/edit/$', views.GroupUpdate.as_view(), name='group_edit'),
                       url(r'^(?P<pk>\d+)/delete/$', views.GroupDelete.as_view(), name='group_delete'),
                       url(r'^grouplistingtable/', views.GroupListingTable.as_view(), name='GroupListingTable'))
