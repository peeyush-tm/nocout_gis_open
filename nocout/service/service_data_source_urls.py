from django.conf.urls import patterns, url
from service import views

urlpatterns = patterns('',
  url(r'^$', views.ServiceDataSourceList.as_view(), name='service_data_sources_list'),
  url(r'^(?P<pk>\d+)$', views.ServiceDataSourceDetail.as_view(), name='service_parameter_detail'),
  url(r'^new/$', views.ServiceDataSourceCreate.as_view(), name='service_parameter_new'),
  url(r'^edit/(?P<pk>\d+)$', views.ServiceDataSourceUpdate.as_view(), name='service_parameter_edit'),
  url(r'^delete/(?P<pk>\d+)$', views.ServiceDataSourceDelete.as_view(), name='service_parameter_delete'),
  url(r'^ServiceDataSourcelist/', views.ServiceDataSourceListingTable.as_view(), name='ServiceDataSourceListingTable'),
)