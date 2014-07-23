from django.conf.urls import patterns, url
from service import views

urlpatterns = patterns('',
  url(r'^$', views.ServiceHistoryList.as_view(), name='service_history_list'),
  url(r'^serviceparameterslist/', views.ServiceHistoryListingTable.as_view(), name='ServiceHistoryListingTable'),
)