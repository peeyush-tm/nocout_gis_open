from django.conf.urls import patterns, url
from inventory import views

urlpatterns = patterns('',
  url(r'^$', views.ServiceThematicSettingsList.as_view(), name='service_thematic_settings_list'),
  url(r'^(?P<type>((?!new)..)[a-z]+)/$', views.ServiceThematicSettingsList.as_view(), name='service_thematic_settings_list'),
  url(r'^new/$', views.ServiceThematicSettingsCreate.as_view(), name='service_thematic_settings_new'),
  url(r'^(?P<pk>\d+)/edit/$', views.ServiceThematicSettingsUpdate.as_view(), name='service_thematic_settings_edit'),
  url(r'^(?P<pk>\d+)/delete/$', views.ServiceThematicSettingsDelete.as_view(), name='service_thematic_settings_delete'),
  url(r'^ServiceThematicSettingslistingtable/(?P<technology>\w+)/$', views.ServiceThematicSettingsListingTable.as_view(), name='ServiceThematicSettingsListingTable'),
)
