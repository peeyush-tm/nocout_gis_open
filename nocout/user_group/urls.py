from django.conf.urls import patterns, url
from user_group import views

urlpatterns = patterns('',
  url(r'^$', views.UserGroupList.as_view(), name='ug_list'),
  url(r'^(?P<pk>\d+)$', views.UserGroupDetail.as_view(), name='ug_detail'),
  url(r'^new/$', views.UserGroupCreate.as_view(), name='ug_new'),
  url(r'^edit/(?P<pk>\d+)$', views.UserGroupUpdate.as_view(), name='ug_edit'),
  url(r'^delete/(?P<pk>\d+)$', views.UserGroupDelete.as_view(), name='ug_delete'),
  url(r'usergrouplistingtable/', views.UserGroupListingTable.as_view(), name= 'UserGroupListingTable'),
  url(r'user_group_users_wrt_organization/', views.user_group_users_render_wrt_organization, name= 'user_group_users_wrt_organization')
)