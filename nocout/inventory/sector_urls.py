from django.conf.urls import patterns, url
from inventory import views

urlpatterns = patterns('',
  url(r'^$', views.SectorList.as_view(), name='sectors_list'),
  url(r'^(?P<pk>\d+)$', views.SectorDetail.as_view(), name='sector_detail'),
  url(r'^new/$', views.SectorCreate.as_view(), name='sector_new'),
  url(r'^edit/(?P<pk>\d+)$', views.SectorUpdate.as_view(), name='sector_edit'),
  url(r'^delete/(?P<pk>\d+)$', views.SectorDelete.as_view(), name='sector_delete'),
  url(r'^Sectorlistingtable/', views.SectorListingTable.as_view(), name='SectorListingTable'),
  url(r'^list/sector/$', views.list_sector, name='list-sector'),
  url(r'^select/sector/(?P<pk>\d+)/$', views.select_sector, name='select-sector'),
)
