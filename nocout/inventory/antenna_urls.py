from django.conf.urls import patterns, url
from inventory import views

urlpatterns = patterns('',
  url(r'^$', views.AntennaList.as_view(), name='antennas_list'),
  url(r'^(?P<pk>\d+)/$', views.AntennaDetail.as_view(), name='antenna_detail'),
  url(r'^new/$', views.AntennaCreate.as_view(), name='antenna_new'),
  url(r'^(?P<pk>\d+)/edit/$', views.AntennaUpdate.as_view(), name='antenna_edit'),
  url(r'^(?P<pk>\d+)/delete/$', views.AntennaDelete.as_view(), name='antenna_delete'),
  url(r'^Antennalistingtable/', views.AntennaListingTable.as_view(), name='AntennaListingTable'),
  url(r'^list/antenna/$', views.list_antenna, name='list-antenna'),
  url(r'^select/antenna/(?P<pk>\d+)/$', views.select_antenna, name='select-antenna'),
)
