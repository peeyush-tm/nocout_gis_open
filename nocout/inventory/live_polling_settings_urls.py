from django.conf.urls import patterns, url
from inventory import views

urlpatterns = patterns('',
  url(r'^$', views.LivePollingSettingsList.as_view(), name='live_polling_settings_list'),
  url(r'^(?P<pk>\d+)/$', views.LivePollingSettingsDetail.as_view(), name='live_polling_settings_detail'),
  url(r'^new/$', views.LivePollingSettingsCreate.as_view(), name='live_polling_settings_new'),
  url(r'^(?P<pk>\d+)/edit/$', views.LivePollingSettingsUpdate.as_view(), name='live_polling_settings_edit'),
  url(r'^(?P<pk>\d+)/delete/$', views.LivePollingSettingsDelete.as_view(), name='live_polling_settings_delete'),
  url(r'^LivePollingSettingslistingtable/', views.LivePollingSettingsListingTable.as_view(), name='LivePollingSettingsListingTable'),
)
