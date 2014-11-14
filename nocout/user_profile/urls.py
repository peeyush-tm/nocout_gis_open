from django.conf.urls import patterns, url
from user_profile import views

urlpatterns = patterns('',
  url(r'^$', views.UserList.as_view(), name='user_list'),
  url(r'^(?P<pk>\d+)/$', views.UserDetail.as_view(), name='user_detail'),
  url(r'^new/$', views.UserCreate.as_view(), name='user_new'),
  url(r'^(?P<pk>\d+)/edit/$', views.UserUpdate.as_view(), name='user_edit'),
  url(r'^(?P<pk>\d+)/delete/$', views.UserDelete.as_view(), name='user_delete'),
  url(r'^myprofile/', views.CurrentUserProfileUpdate.as_view(), name='current_user_profile_update'),
  url(r'userlistingtable/', views.UserListingTable.as_view(), name= 'UserListingTable'),
  url(r'userarchivedlistingtable/', views.UserArchivedListingTable.as_view(), name= 'UserArchivedListingTable'),
  url(r'organisation/user/list/$', views.organisation_user_list, name= 'organisation-user-list'),
  url(r'organisation/user/select/$', views.organisation_user_select, name= 'organisation-user-select'),

)
