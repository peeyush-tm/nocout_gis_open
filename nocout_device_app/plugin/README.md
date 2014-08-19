Poller scripts(Plugins)

Base directory for all poller scripts for radwin devices

1. Files List
=================================
|-- radwin_autonegotiation_status
|-- radwin_cbw_invent
|-- radwin_dl_utilization
|-- radwin_frequency_invent
|-- radwin_idu_sn_invent
|-- radwin_link_distance_invent
|-- radwin_link_ethernet_status
|-- radwin_mimo_diversity_invent
|-- radwin_odu_sn_invent
|-- radwin_port_mode_status
|-- radwin_port_speed_status
|-- radwin_producttype_invent
|-- radwin_rssi
|-- radwin_service_throughput
|-- radwin_ssid_invent
|-- radwin_sync_state_status
|-- radwin_uas
|-- radwin_ul_utilization
|-- radwin_uptime
`-- README.md

2. Description
Poller scripts are cataegriozed as follwing:
     1. services(device parameters) which run on 5 min interval (without _invent or _status )
     2. services(device parameters) which run on 1 hour interval ends with _status
     3. services(device parameters) which run on 1 day interval  ends with _invent
=================================
1. radwin_autonegotiation_status: This plugin retrieves the device port auto negotitation state 
2. radwin_cbw_invent: This plugin retrieves the current channel bandwidth associated with device
3. radwin_dl_utilization: Plugin retrieves the total port downlink utilization
4. radwin_frequency_invent: Plugin retrievs the operating frequency of device
5. radwin_idu_sn_invent: Plugin retrieves the idu serial number
6. radwin_link_distance_invent: Plugin retrieves the link distance between BS
7. radwin_link_ethernet_status: Plugin retrieves the port ethernet status.
8. radwin_mimo_diversity_invent: Plugin retrives the transmission type.
9. radwin_odu_sn_invent: Plugin retrieves the ODU serial number
10. radwin_port_mode_status: Plugin retrieves the port duplex type status
11. radwin_port_speed_status: Plugin retrieves the port speed status
12. radwin_producttype_invent : Plugin retrieves the producttype of device
13. radwin_rssi: Received signal strength of device in 5 min interval
14. radwin_service_throughput: total service throughput of device in 5 min interval
15. radwin_ssid_invent: : Retrieves the device ssid
17. radwin_sync_state_status: Retrieves the master slave sync state
18. radwin_uas: Retrieves the unavailable seconds parameter value
19. radwin_ul_utilization: Retrieves the port uplink utilization parmeter value
20. radwin_uptime: total uptime for the device

3. Files Path
========================================
/apps/omd/sites/<site_name>/nocout/plugin/





