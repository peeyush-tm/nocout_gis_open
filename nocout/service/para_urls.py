from django.conf.urls import patterns, url
from service import views

urlpatterns = patterns('',
  url(r'^$', views.ServiceParametersList.as_view(), name='services_parameter_list'),
  url(r'^(?P<pk>\d+)/$', views.ServiceParametersDetail.as_view(), name='service_parameter_detail'),
  url(r'^new/$', views.ServiceParametersCreate.as_view(), name='service_parameter_new'),
  url(r'^(?P<pk>\d+)/edit/$', views.ServiceParametersUpdate.as_view(), name='service_parameter_edit'),
  url(r'^(?P<pk>\d+)/delete/$', views.ServiceParametersDelete.as_view(), name='service_parameter_delete'),
  url(r'^serviceparameterslist/', views.ServiceParametersListingTable.as_view(), name='ServiceParametersListingTable'),
)
