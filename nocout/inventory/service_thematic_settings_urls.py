from django.conf.urls import patterns, url
from inventory import views

urlpatterns = patterns('',
  url(r'^$', views.ServiceThematicSettingsList.as_view(), name='service_thematic_settings_list'),
  url(r'^(?P<type>((?!new)..)[a-z]+)/$', views.ServiceThematicSettingsList.as_view(), name='service_thematic_settings_list'),
  url(r'^new/$', views.ServiceThematicSettingsCreate.as_view(), name='service_thematic_settings_new'),
  url(r'^edit/(?P<pk>\d+)$', views.ServiceThematicSettingsUpdate.as_view(), name='service_thematic_settings_edit'),
  url(r'^delete/(?P<pk>\d+)$', views.ServiceThematicSettingsDelete.as_view(), name='service_thematic_settings_delete'),
  url(r'^ServiceThematicSettingslistingtable/(?P<technology>\w+)$', views.ServiceThematicSettingsListingTable.as_view(), name='ServiceThematicSettingsListingTable'),
)
