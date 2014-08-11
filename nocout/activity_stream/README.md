Module: Activity Stream
===

```
Activity Stream is module for capturing the user interaction with the Nocout User Application.
The Activity Stream module captures the 
1. Module user has interacted with
2. Values changed by the user in any module
The Activity stream needs to be configured in "settings.py" file carrying the settings for application in the folder
nocout/settings.py
```

List of modules monitored are as follows:
---

 - 'auth.user',
 - 'auth.group',
 - 'sites.site',
 - 'comments.comment',
 - 'user_profile.userprofile',
 - 'user_group.usergroup',
 - 'device.device',
 - 'device_group.devicegroup',
 - 'device.devicetypefields',
 - 'device.devicetechnology',
 - 'device.devicevendor',
 - 'device.devicemodel',
 - 'device.devicetype',
 - 'site_instance.siteinstance',
 - 'service.service',
 - 'service.serviceparameters',
 - 'command.command',
 - 'organization.organization','inventory.inventory',
 - 'inventory.antenna',
 - 'inventory.basestation',
 - 'inventory.sector',
 - 'inventory.backhaul',
 - 'inventory.customer',
 - 'inventory.substation',
 - 'inventory.circuit',
 - 'machine.machine',
 - 'service.servicedatasource',
 - 'device.deviceport',
 - 'device.devicefrequency',
 - 'service.protocol',
 - 'inventory.iconsettings',
 - 'inventory.livepollingsettings',
 - 'inventory.thresholdconfiguration',
 - 'inventory.thematicsettings'


Activity Stream Settings
---

```
ACTSTREAM_SETTINGS = {
    'MODELS': ('auth.user', 'auth.group', 'sites.site', 'comments.comment','user_profile.userprofile', 'user_group.usergroup',
                'device.device', 'device_group.devicegroup', 'device.devicetypefields','device.devicetechnology',
                'device.devicevendor', 'device.devicemodel', 'device.devicetype','site_instance.siteinstance','service.service',
                'service.serviceparameters','command.command','organization.organization','inventory.inventory',
                'inventory.antenna', 'inventory.basestation', 'inventory.sector', 'inventory.backhaul', 'inventory.customer',
                'inventory.substation', 'inventory.circuit', 'machine.machine', 'service.servicedatasource', 'device.deviceport',
                'device.devicefrequency', 'service.protocol', 'inventory.iconsettings', 'inventory.livepollingsettings',
                'inventory.thresholdconfiguration', 'inventory.thematicsettings'),




    'MANAGER': 'actstream.managers.ActionManager',
    'FETCH_RELATIONS': True,
    'USE_PREFETCH': True,
    'USE_JSONFIELD': True,
    'GFK_FETCH_DEPTH': 1,

}
```
