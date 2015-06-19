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
    url(r'^device_restore_display_data/(?P<value>\d+)/$', api.DeviceRestoreDispalyData.as_view()),
    url(r'^restore_device/(?P<pk>\d+)/$', api.RestoreDevice.as_view()),
    url(r'^add_device_to_nms_display_info/(?P<pk>\d+)/$', api.AddDeviceToNMSDisplayInfo.as_view()),
    url(r'^add_device_to_nms/(?P<pk>\d+)/', api.AddDeviceToNMS.as_view()),
]
