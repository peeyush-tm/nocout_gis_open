from django.conf.urls import patterns, url
from service import views

urlpatterns = patterns('',
  url(r'^$', views.ProtocolList.as_view(), name='protocols_list'),
  url(r'^(?P<pk>\d+)$', views.ProtocolDetail.as_view(), name='protocol_detail'),
  url(r'^new/$', views.ProtocolCreate.as_view(), name='protocol_new'),
  url(r'^edit/(?P<pk>\d+)$', views.ProtocolUpdate.as_view(), name='protocol_edit'),
  url(r'^delete/(?P<pk>\d+)$', views.ProtocolDelete.as_view(), name='protocol_delete'),
  url(r'^Protocollist/', views.ProtocolListingTable.as_view(), name='ProtocolListingTable'),
)