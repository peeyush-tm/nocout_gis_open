from django.conf.urls import patterns, include, url
from .views import dialog_action, UserStatusList, UserStatusTable, change_user_status


urlpatterns = patterns('',
                       url(r'^$',UserStatusList.as_view(), name='sm_list'),
                       url(r'userstatustable/', UserStatusTable.as_view(), name= 'UserStatusTable'),
                       url(r'^dialog_action/$', dialog_action),
                       url(r'^change_user_status/$', change_user_status),

                       )