from django.conf.urls import patterns, url
from inventory import views

urlpatterns = patterns('',
  url(r'^$', views.PingThematicSettingsList.as_view(), name='ping_thematic_settings_list'),
  url(r'^(?P<type>((?!new)..)[a-z]+)/$', views.PingThematicSettingsList.as_view(), name='ping_thematic_settings_list'),
  url(r'^new/$', views.PingThematicSettingsCreate.as_view(), name='ping_thematic_settings_new'),
  url(r'^edit/(?P<pk>\d+)$', views.PingThematicSettingsUpdate.as_view(), name='ping_thematic_settings_edit'),
  url(r'^delete/(?P<pk>\d+)$', views.PingThematicSettingsDelete.as_view(), name='ping_thematic_settings_delete'),
  url(r'^PingThematicSettingslistingtable/(?P<technology>\w+)$', views.PingThematicSettingsListingTable.as_view(), name='PingThematicSettingsListingTable'),
  url(r'^ping_user_thematic_setting/', views.Ping_Update_User_Thematic_Setting.as_view(),
      name='ping_user_thematic_setting')
)