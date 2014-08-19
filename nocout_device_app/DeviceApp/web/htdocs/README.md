DeviceApp
=========

Base staging directory for Network monitoring core configuration


I. Files List
-------------
.
|-- ./nocout_live.py
|-- ./nocout.py
`-- ./README.md

II. Description
---------------

nocout_live.py :: 
	This web script handles the live polling mechanism.
Live polling returns the current value for a data source of a service.
e.g. for service radwin_rssi current value for rssi parameter could be retrieved.

nocout.py ::
	This web script configures the devices in Nagios for monitoring and schedules
different services on those devices.

III. File Location
------------------

nocout_live.py :: /apps/opt/omd/sites/master_UA/share/check_mk/web/htdocs/

nocout.py :: /apps/opt/omd/sites/master_UA/share/check_mk/web/htdocs/


