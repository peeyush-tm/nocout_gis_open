from django.conf.urls import patterns, url
import views

urlpatterns = patterns('',
  url(r'^$', views.SNMPTrapSettingsList.as_view(), name='snmp_trap_settings_list'),
  url(r'^(?P<pk>\d+)/$', views.SNMPTrapSettingsDetail.as_view(), name='snmp_trap_settings_detail'),
  url(r'^new/$', views.SNMPTrapSettingsCreate.as_view(), name='snmp_trap_settings_new'),
  url(r'^(?P<pk>\d+)/edit/$', views.SNMPTrapSettingsUpdate.as_view(), name='snmp_trap_settings_edit'),
  url(r'^(?P<pk>\d+)/delete/$', views.SNMPTrapSettingsDelete.as_view(), name='snmp_trap_settings_delete'),
  url(r'^SNMPTrapSettingslistingtable/', views.SNMPTrapSettingsListingTable.as_view(), name='SNMPTrapSettingsListingTable'),
  url(r'^select2/elements/$', views.SelectSNMPTrapSettingsListView.as_view(), name='select2-snmp_trap_settings-elements'),
)
