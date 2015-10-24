from django.conf.urls import url
import api

urlpatterns = [
    url(r'^user_soft_delete_display_data/(?P<value>\d+)/$', api.UserSoftDeleteDisplayData.as_view(),
        name='user_soft_delete_display_data'),
    url(r'^user_soft_delete/(?P<value>\d+)/(?P<new_parent_id>\d+)/$', api.UserSoftDelete.as_view(),
        name='user_soft_delete'),
    url(r'^restore_user/(?P<value>\d+)/$', api.RestoreUser.as_view(), name='restore_user'),
    url(r'^delete_user/(?P<value>\d+)/$', api.DeleteUser.as_view(), name='delete_user'),
    url(r'^reset_user_permissions/(?P<value>\d+)/$', api.ResetUserPermissions.as_view(), name='reset_user_permissions'),
]
