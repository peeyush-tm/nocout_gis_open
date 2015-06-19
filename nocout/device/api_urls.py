from django.conf.urls import url
import api

urlpatterns = [
    url(r'^get_tech_vendors/(?P<pk>\d+)/$', api.GetVendorsForTech.as_view()),
    url(r'^get_vendor_models/(?P<pk>\d+)/$', api.GetModelsForVendor.as_view()),
    url(r'^get_model_types/(?P<pk>\d+)/$', api.GetModelsForVendor.as_view()),
    url(r'^get_device_ports/(?P<pk>\d+)/$', api.GetDevicePorts.as_view()),
    url(r'^get_machine_sites/(?P<pk>\d+)/$', api.GetSitesForMachine.as_view()),
    url(r'^get_extra_fields/(?P<pk>\d+)/$', api.GetDeviceTypeExtraFields.as_view()),
    url(r'^devices_for_menu/(?P<flag>\w+)/$', api.GetDevicesForSelectionMenu.as_view()),
    url(r'^device_inventory/(?P<flag>\w+)/$', api.GetDeviceInventory.as_view()),
    url(r'^get_eligible_parent/(?P<pk>\d+)/$', api.GetEligibleParentDevices.as_view()),
    url(r'^device_soft_delete/(?P<device_id>\d+)(?:/(?P<new_parent_id>\d+))?/$', api.DeviceSoftDelete.as_view()),
    url(r'^device_restore_display_aa/(?P<value>\d+)/$', api.DeviceRestoreDispalyData.as_view()),
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
]
