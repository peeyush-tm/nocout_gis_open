from django.conf.urls import patterns, url
from .views import *


urlpatterns = patterns('',
                       url(r'^$',UserStatusList.as_view(), name='sm_list'),
                       url(r'userstatustable/', UserStatusTable.as_view(), name= 'UserStatusTable'),
                       url(r'^dialog_action/$', dialog_action),
                       url(r'^change_user_status/$', change_user_status),
                       url(r'^dialog_for_page_refresh/$', dialog_for_page_refresh),
                       url(r'^dialog_expired_logout_user/$', dialog_expired_logout_user),
                       url(r'^logout_user/$', logout_user),
                       )