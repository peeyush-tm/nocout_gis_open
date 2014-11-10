from django.conf.urls import patterns, url
from inventory import views

urlpatterns = patterns('',
  url(r'^$', views.BackhaulList.as_view(), name='backhauls_list'),
  url(r'^(?P<pk>\d+)$', views.BackhaulDetail.as_view(), name='backhaul_detail'),
  url(r'^new/$', views.BackhaulCreate.as_view(), name='backhaul_new'),
  url(r'^edit/(?P<pk>\d+)$', views.BackhaulUpdate.as_view(), name='backhaul_edit'),
  url(r'^delete/(?P<pk>\d+)$', views.BackhaulDelete.as_view(), name='backhaul_delete'),
  url(r'^Backhaullistingtable/', views.BackhaulListingTable.as_view(), name='BackhaulListingTable'),
  url(r'^list/backhaul/$', views.list_backhaul, name='list_-backhaul'),
  url(r'^select/backhaul/(?P<pk>\d+)/$', views.select_backhaul, name='select-backhaul'),
)
