from django.conf.urls import patterns, url
from download_center import views, api

urlpatterns = patterns('',
                       url(r'^$', views.CityCharterSettingsView.as_view(),
                           name='city_charter_settings'),
                       url(r'^get_current_cc_settings/', api.FetchCityCharterSettings.as_view()),
                       )
