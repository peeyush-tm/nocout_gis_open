from django.conf.urls import patterns, url
from machine import views

urlpatterns = patterns('',
    url(r'^$', views.MachineList.as_view(), name='machines_list'),
    url(r'^(?P<pk>\d+)$', views.MachineDetail.as_view(), name='machine_detail'),
    url(r'^new/$', views.MachineCreate.as_view(), name='machine_new'),
    url(r'^edit/(?P<pk>\d+)$', views.MachineUpdate.as_view(), name='machine_edit'),
    url(r'^delete/(?P<pk>\d+)$', views.MachineDelete.as_view(), name='machine_delete'),
    url(r'Machinelistingtable/', views.MachineListingTable.as_view(), name= 'MachineListingTable')

    )