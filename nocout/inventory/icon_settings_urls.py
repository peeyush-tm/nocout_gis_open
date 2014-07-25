from django.conf.urls import patterns, url
from inventory import views

urlpatterns = patterns('',
  url(r'^$', views.IconSettingsList.as_view(), name='icon_settings_list'),
  url(r'^(?P<pk>\d+)$', views.IconSettingsDetail.as_view(), name='icon_settings_detail'),
  url(r'^new/$', views.IconSettingsCreate.as_view(), name='icon_settings_new'),
  url(r'^edit/(?P<pk>\d+)$', views.IconSettingsUpdate.as_view(), name='icon_settings_edit'),
  url(r'^delete/(?P<pk>\d+)$', views.IconSettingsDelete.as_view(), name='icon_settings_delete'),
  url(r'^IconSettingslistingtable/', views.IconSettingsListingTable.as_view(), name='IconSettingsListingTable'),
)