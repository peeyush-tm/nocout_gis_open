from django.conf.urls import patterns, url
from command import views

urlpatterns = patterns('',
    url(r'^$', views.CommandList.as_view(), name='commands_list'),
    url(r'^(?P<pk>\d+)$', views.CommandDetail.as_view(), name='command_detail'),
    url(r'^new/$', views.CommandCreate.as_view(), name='command_new'),
    url(r'^edit/(?P<pk>\d+)$', views.CommandUpdate.as_view(), name='command_edit'),
    url(r'^delete/(?P<pk>\d+)$', views.CommandDelete.as_view(), name='command_delete'),
    url(r'^commandlistingtable/', views.CommandListingTable.as_view(), name='CommandListingTable'),
)