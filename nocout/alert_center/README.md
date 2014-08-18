ALERT CENTER
===

```
Alert Center module is for displaying the Alerts, Alarms and Events of the Devices in User's Organisation Inventory.
Alarms : Device SNMP Traps
Event  : Device Service Threshold Breach and Restore Events
```

Network Alert Center
---

```
Network Alert Center provides a comprehensive details for all the Base Station Events
```

1. Latency               : The PING RTA related Event Details
2. Packet Drop           : The PING packet drop related Event Details
3. Down                  : The Devices with 100% Packet Loss or Very High RTA
4. Service Impact Alarms : The Events for monitored services for a device

Customer Alert Center
---

```
Alert Category for Sub-Station Events
```

1. PTP   : PTP type device Events
2. WiMAX : WiMAX type device Events
3. PMP   : PMP type device Events


Alert Details
---

```
Alert Details are the various categorized alerts for a device in SS or BS or back haul
```

##Network Details


```
Provides category wise Alert Details for BS type devices and BackHaul type devices
```

1. Temperature          : Alarms for Temperature threshold breaches for a network element
2. Wimax BS             : All the Alarms for Wimax BS type elements
3. PMP BS               : All the Alarms for PMP BS type elements
4. Converter            : All the Alarms for Sector Configured on Converter type elements
5. UL Issue             : All the Alarms for UL issues for BS type elements
6. Sector Utilisation   : All the Alarms for Sector Configured on type elements
7. BH Utilisation       : All the Alarms for BH Configured on type elements

##Customer Details


```
Alert Category for Sub-Station Events
```

1. PTP   : PTP type device Events
2. WiMAX : WiMAX type device Events
3. PMP   : PMP type device Events


Module Files
===

```
.
├── README.md
├── __init__.py
├── admin.py
├── docs
│   ├── ALERT CENTER.html
│   └── ALERT CENTER.pdf
├── models.py
├── templates
│   └── alert_center
│       ├── customer_alerts_list.html
│       ├── customer_details_list.html
│       ├── network_alerts_list.html
│       ├── network_details_list.html
│       └── single_device_alert.html
├── tests.py
├── urls.py
└── views.py
```

1. README.md    : Module's README file for details
2. __init.py__  : Python's modules init file
3. admin.py     : Django Framework's Admin module registration file
4. docs         : Documentation folder for the module
5. models.py    : Django Framework's database interface
6. templates    : HTML files for rendering a View for the module
7. tests.py     : unit test files for the module
8. urls.py      : Module's url routing file
9. views.py     : Modules controller file