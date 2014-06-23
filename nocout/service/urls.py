from django.conf.urls import patterns, url
from service import views

urlpatterns = patterns('',
  url(r'^$', views.ServiceList.as_view(), name='services_list'),
  url(r'^(?P<pk>\d+)$', views.ServiceDetail.as_view(), name='service_detail'),
  url(r'^new/$', views.ServiceCreate.as_view(), name='service_new'),
  url(r'^edit/(?P<pk>\d+)$', views.ServiceUpdate.as_view(), name='service_edit'),
  url(r'^delete/(?P<pk>\d+)$', views.ServiceDelete.as_view(), name='service_delete'),
  url(r'^servicelistingtable/', views.ServiceListingTable.as_view(), name='ServiceListingTable'),
)