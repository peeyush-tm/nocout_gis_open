from django.conf.urls import patterns, url
from inventory import views

urlpatterns = patterns('',
  url(r'^$', views.CustomerList.as_view(), name='customers_list'),
  url(r'^(?P<pk>\d+)$', views.CustomerDetail.as_view(), name='customer_detail'),
  url(r'^new/$', views.CustomerCreate.as_view(), name='customer_new'),
  url(r'^edit/(?P<pk>\d+)$', views.CustomerUpdate.as_view(), name='customer_edit'),
  url(r'^delete/(?P<pk>\d+)$', views.CustomerDelete.as_view(), name='customer_delete'),
  url(r'^Customerlistingtable/', views.CustomerListingTable.as_view(), name='CustomerListingTable'),
)