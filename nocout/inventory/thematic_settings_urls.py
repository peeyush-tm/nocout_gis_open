from django.conf.urls import patterns, url
from inventory import views

urlpatterns = patterns('',
  url(r'^$', views.ThematicSettingsList.as_view(), name='thematic_settings_list'),
  url(r'^(?P<pk>\d+)$', views.ThematicSettingsDetail.as_view(), name='thematic_settings_detail'),
  url(r'^new/$', views.ThematicSettingsCreate.as_view(), name='thematic_settings_new'),
  url(r'^edit/(?P<pk>\d+)$', views.ThematicSettingsUpdate.as_view(), name='thematic_settings_edit'),
  url(r'^delete/(?P<pk>\d+)$', views.ThematicSettingsDelete.as_view(), name='thematic_settings_delete'),
  url(r'^ThematicSettingslistingtable/', views.ThematicSettingsListingTable.as_view(), name='ThematicSettingsListingTable'),
)