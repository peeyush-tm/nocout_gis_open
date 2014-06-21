from django.conf.urls import patterns, url
from inventory import views

urlpatterns = patterns('',
  url(r'^$', views.AntennaList.as_view(), name='antennas_list'),
  url(r'^(?P<pk>\d+)$', views.AntennaDetail.as_view(), name='antenna_detail'),
  url(r'^new/$', views.AntennaCreate.as_view(), name='antenna_new'),
  url(r'^edit/(?P<pk>\d+)$', views.AntennaUpdate.as_view(), name='antenna_edit'),
  url(r'^delete/(?P<pk>\d+)$', views.AntennaDelete.as_view(), name='antenna_delete'),
  url(r'^Antennalistingtable/', views.AntennaListingTable.as_view(), name='AntennaListingTable'),
)