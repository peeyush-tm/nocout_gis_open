from django.conf.urls import url
import api

urlpatterns = [
    url(r'^get_tech_vendors/(?P<pk>\d+)/$', api.GetVendorsForTech.as_view(), name='get_vendors_for_tech'),
    url(r'^get_vendor_models/(?P<pk>\d+)/$', api.GetModelsForVendor.as_view(), name='get_models_for_vendor'),
    url(r'^get_model_types/(?P<pk>\d+)/$', api.GetTypesForModel.as_view(), name='get_types_for_model'),
    url(r'^get_device_ports/(?P<pk>\d+)/$', api.GetDevicePorts.as_view()),
    url(r'^get_machine_sites/(?P<pk>\d+)/$', api.GetSitesForMachine.as_view(), name='get_sites_for_machine'),
    url(r'^get_extra_fields/(?P<pk>\d+)/$', api.GetDeviceTypeExtraFields.as_view()),
    url(r'^devices_for_menu/(?P<flag>\w+)/$', api.GetDevicesForSelectionMenu.as_view()),
    url(r'^device_inventory/(?P<flag>\w+)/$', api.GetDeviceInventory.as_view()),
    url(r'^get_eligible_parent/(?P<pk>\d+)/$', api.GetEligibleParentDevices.as_view()),
    url(r'^device_soft_delete/(?P<device_id>\d+)(?:/(?P<new_parent_id>\d+))?/$', api.DeviceSoftDelete.as_view()),
    url(r'^device_restore_display_data/(?P<value>\d+)/$', api.DeviceRestoreDispalyData.as_view()),
    url(r'^restore_device/(?P<pk>\d+)/$', api.RestoreDevice.as_view()),
    url(r'^add_device_to_nms_display_info/(?P<pk>\d+)/$', api.AddDeviceToNMSDisplayInfo.as_view()),
    url(r'^add_device_to_nms/(?P<pk>\d+)/', api.AddDeviceToNMS.as_view()),
    url(r'^edit_device_in_nms/(?P<pk>\d+)/$', api.EditDeviceInNMS.as_view()),
    url(r'^delete_device_from_nms/(?P<pk>\d+)/$', api.DeleteDeviceFromNMS.as_view()),
    url(r'^modify_device_state/(?P<pk>\d+)/$', api.ModifyDeviceState.as_view()),
    url(r'^sync_devices_in_nms/(?P<pk>\d+)/$', api.SyncDevicesInNMS.as_view()),
    url(r'^remove_sync_deadlock/(?P<pk>\d+)/$', api.RemoveSyncDeadlock.as_view()),
    url(r'^edit_single_svc_display_data/(?P<dsc_id>\d+)/$', api.EditSingleServiceDisplayData.as_view()),
    url(r'^get_svc_para_table_data/(?P<device_name>\w+)/(?P<service_name>\w+)/(?P<template_id>\d+)/$',
        api.GetServiceParaTableData.as_view()),
    url(r'^edit_single_service/(?P<dsc_id>\d+)/(?P<svc_temp_id>\d+)/', api.EditSingleService.as_view()),
    url(r'^delete_single_svc_display_data/(?P<dsc_id>\d+)/$', api.DeleteSingleServiceDisplayData.as_view()),
    url(r'^delete_single_svc/(?P<device_name>\w+)/(?P<service_name>\w+)/$', api.DeleteSingleService.as_view()),
    url(r'^edit_svc_display_data/(?P<pk>\d+)/(?P<svc_temp_id>\d+)/', api.EditServiceDisplayData.as_view()),
    url(r'^svc_edit_old_conf/(?P<option>\d+)/(?P<service_id>\d+)/(?P<device_id>\d+)/$',
        api.ServiceEditOldConf.as_view()),
    url(r'^svc_edit_new_conf/(?P<service_id>\d+)/(?P<template_id>\d+)/$', api.ServiceEditNewConf.as_view()),
    url(r'^svc_edit_ping_conf/(?P<pk>\d+)/$', api.ServiceEditPingConf.as_view()),
    url(r'^edit_services/(?P<device_id>\d+)/', api.EditServices.as_view()),
    url(r'^delete_svc_display_data/(?P<pk>\d+)/$', api.DeleteServiceDisplayData.as_view()),
    url(r'^delete_services/(?P<pk>\d+)/', api.DeleteServices.as_view()),
    url(r'^add_svc_display_data/(?P<pk>\d+)/$', api.AddServiceDisplayData.as_view()),
    url(r'^svc_add_old_conf/(?P<device_id>\d+)/(?P<service_id>\d+)/(?P<option>\d+)/$',
        api.ServiceAddOldConf.as_view()),
    url(r'^svc_add_new_conf/(?P<service_id>\d+)/(?P<template_id>\d+)/$',
        api.ServiceAddNewConf.as_view()),
    url(r'^add_services/(?P<device_id>\d+)/', api.AddServices.as_view()),
    url(r'^device_service_status/(?P<pk>\d+)/$', api.DeviceServiceStatus.as_view()),
    url(r'^reset_service_conf/$', api.ResetServiceConfiguration.as_view()),
]
