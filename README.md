nocout_gis
==========

GIS Inventory Nocout

Installation Steps:
---

**Pre-requisits**

1. Linux System (Ubuntu 12.04 LTS)
2. Python Virtualenv (sudo aptitude install python-virtualenv)
3. OMDdistro
4. Install MariaDB or MySQL
    1. If the installation is with mysql : sudo aptitude install mysqlclient-dev libmysqlclient-dev
    2. If the installation is with mariadb : sudo aptitude install mariadbclient-dev libmariadbclient-dev
5. Install python-dev - sudo aptitude install python-dev 
6. Install phpmyadmin
7. Create a database named : nocout_dev
8. Install graphviz -  sudo aptitude install graphviz
9. Install Python Wrapper to graphviz - sudo aptitude install python-pygraphviz
10. Install Shared libraries graphviz & python -  sudo aptitude install libgraphviz-dev
12. Install Geometry Engine, Open Source libraries - sudo aptitude install libgeos-dev

**Setup Enviornment**

1. Create folder in /home/<USER>/Document - NOCOUT
2. Change dir - $:~ cd /home/<USER>/Documents/NOCOUT
3. Clone "nocout_gis" repository to this folder (/home/<USER>/Documents/NOCOUT) - $:~ git clone <REPOSITORY-ADDRESS>
4. Go to the cloned repository folder : cd /home/<USER>/Documents/NOCOUT/nocout_gis
5. Create virtualenv - $:~ virtualenv nout
6. Activate virtualenv - (nout):~ source nout/bin/activate
7. Install the requirements for Django app - (nout):~pip install -r requirements.txt 


**Setup Application**

1. Go to folder : /home/<USER>/Documents/NOCOUT/nocout_gis/nocout
2. Run syncdb : python manage.py syncdb --noinput
3. Run migrations : python manage.py migrate
4. Run the data loading fixtures : Load Commands :  python manage.py loaddata fixtures/<FIXTURE NAME>.json


Module Files
===

```
.
├── __init__.py
├── activity_stream
│   ├── README.md
│   ├── __init__.py
│   ├── actions.py
│   ├── admin.py
│   ├── docs
│   │   ├── ActivityStream.html
│   │   └── ActivityStream.pdf
│   ├── models.py
│   ├── templates
│   │   └── activity_stream
│   │       ├── actions_logs.html
│   │       └── hello.html
│   ├── urls.py
│   └── views.py
├── alert_center
│   ├── README.md
│   ├── __init__.py
│   ├── admin.py
│   ├── docs
│   │   ├── ALERT CENTER.html
│   │   └── ALERT CENTER.pdf
│   ├── models.py
│   ├── templates
│   │   └── alert_center
│   │       ├── customer_alerts_list.html
│   │       ├── customer_details_list.html
│   │       ├── network_alerts_list.html
│   │       ├── network_details_list.html
│   │       └── single_device_alert.html
│   ├── tests.py
│   ├── urls.py
│   └── views.py
├── capacity_management
│   ├── __init__.py
│   ├── admin.py
│   ├── models.py
│   ├── templates
│   │   └── capacity_management
│   │       ├── backhaul_capacity_alert.html
│   │       ├── backhaul_capacity_status.html
│   │       ├── sector_capacity_alert.html
│   │       └── sector_capacity_status.html
│   ├── tests.py
│   ├── urls.py
│   └── views.py
├── command
│   ├── __init__.py
│   ├── forms.py
│   ├── migrations
│   │   ├── 0001_initial.py
│   │   └── __init__.py
│   ├── models.py
│   ├── static
│   │   └── css
│   │       └── command.css
│   ├── templates
│   │   └── command
│   │       ├── command_delete.html
│   │       ├── command_detail.html
│   │       ├── command_new.html
│   │       ├── command_update.html
│   │       └── commands_list.html
│   ├── tests.py
│   ├── urls.py
│   └── views.py
├── department
│   ├── __init__.py
│   ├── models.py
│   ├── templates
│   │   └── department
│   │       └── department.html
│   ├── tests.py
│   └── views.py
├── device
│   ├── __init__.py
│   ├── ajax.py
│   ├── api.py
│   ├── device_extra_fields_urls.py
│   ├── device_frequency_urls.py
│   ├── device_model_urls.py
│   ├── device_ports_urls.py
│   ├── device_technology_urls.py
│   ├── device_type_urls.py
│   ├── device_vendor_urls.py
│   ├── forms.py
│   ├── migrations
│   │   ├── 0001_initial.py
│   │   └── __init__.py
│   ├── models.py
│   ├── static
│   │   ├── css
│   │   │   └── device.css
│   │   ├── device
│   │   │   └── css
│   │   │       └── device.css
│   │   └── js
│   │       ├── loadTreeLib.js
│   │       └── nocout_forms.js
│   ├── templates
│   │   ├── device
│   │   │   ├── device_delete.html
│   │   │   ├── device_detail.html
│   │   │   ├── device_new.html
│   │   │   ├── device_update.html
│   │   │   ├── devices_list.html
│   │   │   └── devices_tree_view.html
│   │   ├── device_extra_fields
│   │   │   ├── device_extra_field_delete.html
│   │   │   ├── device_extra_field_detail.html
│   │   │   ├── device_extra_field_new.html
│   │   │   ├── device_extra_field_update.html
│   │   │   └── device_extra_fields_list.html
│   │   ├── device_frequency
│   │   │   ├── device_frequency_delete.html
│   │   │   ├── device_frequency_list.html
│   │   │   ├── device_frequency_new.html
│   │   │   └── device_frequency_update.html
│   │   ├── device_model
│   │   │   ├── device_model_delete.html
│   │   │   ├── device_model_detail.html
│   │   │   ├── device_model_list.html
│   │   │   ├── device_model_new.html
│   │   │   └── device_model_update.html
│   │   ├── device_port
│   │   │   ├── device_port_delete.html
│   │   │   ├── device_port_detail.html
│   │   │   ├── device_port_new.html
│   │   │   ├── device_port_update.html
│   │   │   └── device_ports_list.html
│   │   ├── device_technology
│   │   │   ├── device_technology_delete.html
│   │   │   ├── device_technology_detail.html
│   │   │   ├── device_technology_list.html
│   │   │   ├── device_technology_new.html
│   │   │   └── device_technology_update.html
│   │   ├── device_type
│   │   │   ├── device_type_delete.html
│   │   │   ├── device_type_detail.html
│   │   │   ├── device_type_list.html
│   │   │   ├── device_type_new.html
│   │   │   └── device_type_update.html
│   │   └── device_vendor
│   │       ├── device_vendor_delete.html
│   │       ├── device_vendor_detail.html
│   │       ├── device_vendor_list.html
│   │       ├── device_vendor_new.html
│   │       └── device_vendor_update.html
│   ├── templatetags
│   │   ├── __init__.py
│   │   └── continue_and_break.py
│   ├── tests.py
│   ├── urls.py
│   └── views.py
├── device_group
│   ├── __init__.py
│   ├── admin.py
│   ├── ajax.py
│   ├── forms.py
│   ├── migrations
│   │   ├── 0001_initial.py
│   │   └── __init__.py
│   ├── models.py
│   ├── static
│   │   └── css
│   │       └── device_group.css
│   ├── templates
│   │   └── device_group
│   │       ├── dg_delete.html
│   │       ├── dg_detail.html
│   │       ├── dg_list.html
│   │       ├── dg_new.html
│   │       └── dg_update.html
│   ├── tests.py
│   ├── urls.py
│   └── views.py
├── devicevisualization
│   ├── __init__.py
│   ├── admin.py
│   ├── models.py
│   ├── static
│   │   ├── css
│   │   │   └── style.css
│   │   ├── js
│   │   │   ├── advanceSearchLib.js
│   │   │   ├── devicePlottingLib.js
│   │   │   ├── devicevisualization.js
│   │   │   ├── earth_devicePlottingLib.js
│   │   │   ├── fullScreenControl.js
│   │   │   ├── infobox.js
│   │   │   ├── markerclusterer.js
│   │   │   ├── markerwithlabel.js
│   │   │   └── oms.min.js
│   │   ├── livePolling.json
│   │   ├── new_format.json
│   │   └── services.json
│   ├── templates
│   │   └── devicevisualization
│   │       ├── google_earth_template.html
│   │       └── locate_devices.html
│   ├── tests.py
│   ├── urls.py
│   └── views.py
├── download_center
│   ├── __init__.py
│   ├── admin.py
│   ├── models.py
│   ├── tests.py
│   └── views.py
├── fixtures
│   ├── 14_jul_2014_data_dump_all.txt
│   ├── 14_jul_2014_eve_data_dump_all.txt
│   ├── 15_july_2014_data_dump_all.json
│   ├── 17_july_2014_data_dump_all.json
│   ├── 22_evening_july_2014_data_dump_all.json
│   ├── 22_july_2014_data_dump_all.json
│   ├── 23__july_2014_data_dump_all.json
│   ├── 24_july_default_data.json
│   ├── 25_july_data.json
│   ├── 28_july_fixtures.json
│   ├── 29_july_dump_all.json
│   ├── 31_july_dump_all.json
│   ├── default
│   │   ├── README.txt
│   │   ├── auth.json
│   │   ├── command_default.json
│   │   ├── default_data.json
│   │   ├── device_frequency_default_data.json
│   │   ├── device_group_default.json
│   │   ├── django_user_groups.json
│   │   ├── initial_default_data.json
│   │   ├── inventory_default.json
│   │   ├── inventory_settings.json
│   │   ├── latest_default_data.json
│   │   ├── machine_default.json
│   │   ├── organization_default.json
│   │   ├── service_default.json
│   │   ├── site_instance_default.json
│   │   ├── user_default.json
│   │   └── user_group_default.json
│   ├── default_date_23_july.json
│   ├── geo_data
│   │   ├── README.txt
│   │   ├── city.json
│   │   ├── country.json
│   │   ├── state.json
│   │   └── stategeoinfo.json
│   └── performance
│       └── performance_dump_data.json
├── home
│   ├── __init__.py
│   ├── models.py
│   ├── static
│   │   ├── css
│   │   │   └── nocout_dashboard.css
│   │   └── js
│   │       ├── highcharts.js
│   │       └── nocout_dashboard.js
│   ├── templates
│   │   └── home
│   │       └── home.html
│   ├── tests.py
│   └── views.py
├── inventory
│   ├── __init__.py
│   ├── ajax.py
│   ├── antenna_urls.py
│   ├── backhaul_urls.py
│   ├── base_station_urls.py
│   ├── circuit_urls.py
│   ├── customer_urls.py
│   ├── forms.py
│   ├── icon_settings_urls.py
│   ├── live_polling_settings_urls.py
│   ├── migrations
│   │   ├── 0001_initial.py
│   │   └── __init__.py
│   ├── models.py
│   ├── sector_urls.py
│   ├── sub_station_urls.py
│   ├── templates
│   │   ├── antenna
│   │   │   ├── antenna_delete.html
│   │   │   ├── antenna_detail.html
│   │   │   ├── antenna_list.html
│   │   │   ├── antenna_new.html
│   │   │   └── antenna_update.html
│   │   ├── backhaul
│   │   │   ├── backhaul_delete.html
│   │   │   ├── backhaul_detail.html
│   │   │   ├── backhaul_new.html
│   │   │   ├── backhaul_update.html
│   │   │   └── backhauls_list.html
│   │   ├── base_station
│   │   │   ├── base_station_delete.html
│   │   │   ├── base_station_detail.html
│   │   │   ├── base_station_new.html
│   │   │   ├── base_station_update.html
│   │   │   └── base_stations_list.html
│   │   ├── circuit
│   │   │   ├── circuit_delete.html
│   │   │   ├── circuit_detail.html
│   │   │   ├── circuit_new.html
│   │   │   ├── circuit_update.html
│   │   │   └── circuits_list.html
│   │   ├── customer
│   │   │   ├── customer_delete.html
│   │   │   ├── customer_detail.html
│   │   │   ├── customer_new.html
│   │   │   ├── customer_update.html
│   │   │   └── customers_list.html
│   │   ├── icon_settings
│   │   │   ├── icon_settings_delete.html
│   │   │   ├── icon_settings_detail.html
│   │   │   ├── icon_settings_list.html
│   │   │   ├── icon_settings_new.html
│   │   │   └── icon_settings_update.html
│   │   ├── inventory
│   │   │   ├── inventory.html
│   │   │   ├── inventory_delete.html
│   │   │   ├── inventory_list.html
│   │   │   ├── inventory_new.html
│   │   │   └── inventory_update.html
│   │   ├── live_polling_settings
│   │   │   ├── live_polling_settings_delete.html
│   │   │   ├── live_polling_settings_detail.html
│   │   │   ├── live_polling_settings_list.html
│   │   │   ├── live_polling_settings_new.html
│   │   │   └── live_polling_settings_update.html
│   │   ├── sector
│   │   │   ├── sector_delete.html
│   │   │   ├── sector_detail.html
│   │   │   ├── sector_new.html
│   │   │   ├── sector_update.html
│   │   │   └── sectors_list.html
│   │   ├── sub_station
│   │   │   ├── sub_station_delete.html
│   │   │   ├── sub_station_detail.html
│   │   │   ├── sub_station_new.html
│   │   │   ├── sub_station_update.html
│   │   │   └── sub_stations_list.html
│   │   ├── thematic_settings
│   │   │   ├── thematic_settings_delete.html
│   │   │   ├── thematic_settings_detail.html
│   │   │   ├── thematic_settings_list.html
│   │   │   ├── thematic_settings_new.html
│   │   │   └── thematic_settings_update.html
│   │   └── threshold_configuration
│   │       ├── threshold_configuration_delete.html
│   │       ├── threshold_configuration_detail.html
│   │       ├── threshold_configuration_list.html
│   │       ├── threshold_configuration_new.html
│   │       └── threshold_configuration_update.html
│   ├── tests.py
│   ├── thematic_settings_urls.py
│   ├── threshold_configuration_urls.py
│   ├── urls.py
│   └── views.py
├── machine
│   ├── __init__.py
│   ├── admin.py
│   ├── forms.py
│   ├── migrations
│   │   ├── 0001_initial.py
│   │   └── __init__.py
│   ├── models.py
│   ├── templates
│   │   └── machine
│   │       ├── machine_delete.html
│   │       ├── machine_detail.html
│   │       ├── machine_new.html
│   │       ├── machine_update.html
│   │       └── machines_list.html
│   ├── tests.py
│   ├── urls.py
│   └── views.py
├── manage.py
├── media
├── nocout
│   ├── __init__.py
│   ├── context_processors_profile
│   │   ├── __init__.py
│   │   └── user_profile_atts.py
│   ├── local_settings.py
│   ├── media
│   │   └── icons
│   │       └── 2.jpg
│   ├── middleware.py
│   ├── middlewares
│   │   ├── LoginRequiredMiddleware.py
│   │   └── __init__.py
│   ├── nocout_nginx.conf -> nocout_nginx_https.conf
│   ├── nocout_nginx_http.conf
│   ├── nocout_nginx_https.conf
│   ├── nocout_uwsgi.ini
│   ├── nocout_uwsgi_supervisor.conf
│   ├── settings.py
│   ├── static
│   │   ├── bootstrap-dist
│   │   │   ├── css
│   │   │   │   ├── bootstrap-theme.css
│   │   │   │   ├── bootstrap-theme.min.css
│   │   │   │   ├── bootstrap.css
│   │   │   │   └── bootstrap.min.css
│   │   │   ├── fonts
│   │   │   │   ├── glyphicons-halflings-regular.eot
│   │   │   │   ├── glyphicons-halflings-regular.svg
│   │   │   │   ├── glyphicons-halflings-regular.ttf
│   │   │   │   └── glyphicons-halflings-regular.woff
│   │   │   └── js
│   │   │       ├── bootstrap.js
│   │   │       └── bootstrap.min.js
│   │   ├── css
│   │   │   ├── animatecss
│   │   │   │   └── animate.min.css
│   │   │   ├── cloud-admin.css
│   │   │   ├── cloud-admin.min.css
│   │   │   ├── flags
│   │   │   │   ├── flags.min.css
│   │   │   │   └── flags.png
│   │   │   ├── fonts
│   │   │   │   ├── DXI1ORHCpsQm3Vp6mXoaTXhCUOGz7vYGh680lGh-uXM.woff
│   │   │   │   ├── MTP_ySUJH_bn48VBG8sNSnhCUOGz7vYGh680lGh-uXM.woff
│   │   │   │   ├── cJZKeOuBrn4kERxqtaUH3T8E0i7KZn-EPnyo3HZu7kw.woff
│   │   │   │   └── k3k702ZOKiLJc3WVjuplzHhCUOGz7vYGh680lGh-uXM.woff
│   │   │   ├── inbox.css
│   │   │   ├── nocout_default.css
│   │   │   ├── nocout_forms.css
│   │   │   ├── print.css
│   │   │   ├── responsive.css
│   │   │   ├── responsive.min.css
│   │   │   ├── theme_fonts.css
│   │   │   └── themes
│   │   │       ├── default.css
│   │   │       ├── default.min.css
│   │   │       ├── earth.css
│   │   │       ├── earth.min.css
│   │   │       ├── graphite.css
│   │   │       ├── graphite.min.css
│   │   │       ├── nature.css
│   │   │       ├── nature.min.css
│   │   │       ├── night.css
│   │   │       ├── night.min.css
│   │   │       ├── utopia.css
│   │   │       └── utopia.min.css
│   │   ├── dajax
│   │   │   ├── dojo.dajax.core.js
│   │   │   ├── jquery.dajax.core.js
│   │   │   ├── mootools.dajax.core.js
│   │   │   └── prototype.dajax.core.js
│   │   ├── email_templates
│   │   │   ├── email_template_layout_1.html
│   │   │   ├── email_template_layout_2.html
│   │   │   ├── email_template_layout_3.html
│   │   │   ├── email_template_layout_4.html
│   │   │   ├── email_template_layout_5.html
│   │   │   ├── email_template_layout_6.html
│   │   │   └── email_template_layout_7.html
│   │   ├── font-awesome
│   │   │   ├── css
│   │   │   │   ├── font-awesome.css
│   │   │   │   └── font-awesome.min.css
│   │   │   ├── fonts
│   │   │   │   ├── FontAwesome.otf
│   │   │   │   ├── fontawesome-webfont.eot
│   │   │   │   ├── fontawesome-webfont.svg
│   │   │   │   ├── fontawesome-webfont.ttf
│   │   │   │   └── fontawesome-webfont.woff
│   │   │   ├── less
│   │   │   │   ├── bordered-pulled.less
│   │   │   │   ├── core.less
│   │   │   │   ├── fixed-width.less
│   │   │   │   ├── font-awesome.less
│   │   │   │   ├── icons.less
│   │   │   │   ├── larger.less
│   │   │   │   ├── list.less
│   │   │   │   ├── mixins.less
│   │   │   │   ├── path.less
│   │   │   │   ├── rotated-flipped.less
│   │   │   │   ├── spinning.less
│   │   │   │   ├── stacked.less
│   │   │   │   └── variables.less
│   │   │   └── scss
│   │   │       ├── _bordered-pulled.scss
│   │   │       ├── _core.scss
│   │   │       ├── _fixed-width.scss
│   │   │       ├── _icons.scss
│   │   │       ├── _larger.scss
│   │   │       ├── _list.scss
│   │   │       ├── _mixins.scss
│   │   │       ├── _path.scss
│   │   │       ├── _rotated-flipped.scss
│   │   │       ├── _spinning.scss
│   │   │       ├── _stacked.scss
│   │   │       ├── _variables.scss
│   │   │       └── font-awesome.scss
│   │   ├── fonts
│   │   │   ├── glyphicons-halflings-regular.eot
│   │   │   ├── glyphicons-halflings-regular.svg
│   │   │   ├── glyphicons-halflings-regular.ttf
│   │   │   └── glyphicons-halflings-regular.woff
│   │   ├── frontend_theme
│   │   │   ├── bootstrap-dist
│   │   │   │   ├── css
│   │   │   │   │   ├── bootstrap-theme.css
│   │   │   │   │   ├── bootstrap-theme.min.css
│   │   │   │   │   ├── bootstrap.css
│   │   │   │   │   └── bootstrap.min.css
│   │   │   │   ├── fonts
│   │   │   │   │   ├── glyphicons-halflings-regular.eot
│   │   │   │   │   ├── glyphicons-halflings-regular.svg
│   │   │   │   │   ├── glyphicons-halflings-regular.ttf
│   │   │   │   │   └── glyphicons-halflings-regular.woff
│   │   │   │   └── js
│   │   │   │       ├── bootstrap.js
│   │   │   │       └── bootstrap.min.js
│   │   │   ├── css
│   │   │   │   ├── amimatecss
│   │   │   │   │   └── animate.min.css
│   │   │   │   ├── carousel.css
│   │   │   │   └── cloud-admin-frontend.css
│   │   │   ├── font-awesome
│   │   │   │   ├── css
│   │   │   │   │   ├── font-awesome.css
│   │   │   │   │   └── font-awesome.min.css
│   │   │   │   ├── fonts
│   │   │   │   │   ├── FontAwesome.otf
│   │   │   │   │   ├── fontawesome-webfont.eot
│   │   │   │   │   ├── fontawesome-webfont.svg
│   │   │   │   │   ├── fontawesome-webfont.ttf
│   │   │   │   │   └── fontawesome-webfont.woff
│   │   │   │   ├── less
│   │   │   │   │   ├── bordered-pulled.less
│   │   │   │   │   ├── core.less
│   │   │   │   │   ├── fixed-width.less
│   │   │   │   │   ├── font-awesome.less
│   │   │   │   │   ├── icons.less
│   │   │   │   │   ├── larger.less
│   │   │   │   │   ├── list.less
│   │   │   │   │   ├── mixins.less
│   │   │   │   │   ├── path.less
│   │   │   │   │   ├── rotated-flipped.less
│   │   │   │   │   ├── spinning.less
│   │   │   │   │   ├── stacked.less
│   │   │   │   │   └── variables.less
│   │   │   │   └── scss
│   │   │   │       ├── _bordered-pulled.scss
│   │   │   │       ├── _core.scss
│   │   │   │       ├── _fixed-width.scss
│   │   │   │       ├── _icons.scss
│   │   │   │       ├── _larger.scss
│   │   │   │       ├── _list.scss
│   │   │   │       ├── _mixins.scss
│   │   │   │       ├── _path.scss
│   │   │   │       ├── _rotated-flipped.scss
│   │   │   │       ├── _spinning.scss
│   │   │   │       ├── _stacked.scss
│   │   │   │       ├── _variables.scss
│   │   │   │       └── font-awesome.scss
│   │   │   ├── img
│   │   │   │   ├── Thumbs.db
│   │   │   │   ├── bg.jpg
│   │   │   │   ├── dots.png
│   │   │   │   ├── gallery
│   │   │   │   │   ├── 1.png
│   │   │   │   │   ├── 2.jpg
│   │   │   │   │   ├── 3.png
│   │   │   │   │   ├── 4.png
│   │   │   │   │   ├── 5.png
│   │   │   │   │   ├── 7.jpg
│   │   │   │   │   ├── 8.png
│   │   │   │   │   └── Thumbs.db
│   │   │   │   ├── img1.jpg
│   │   │   │   ├── img2.jpg
│   │   │   │   ├── img3.jpg
│   │   │   │   ├── img4.jpg
│   │   │   │   ├── logo
│   │   │   │   │   ├── Thumbs.db
│   │   │   │   │   ├── cloud.png
│   │   │   │   │   ├── logo-alt.png
│   │   │   │   │   └── logo.png
│   │   │   │   ├── parallax.jpg
│   │   │   │   ├── pattern.png
│   │   │   │   └── testimonials
│   │   │   │       ├── Thumbs.db
│   │   │   │       ├── headshot1.jpg
│   │   │   │       ├── headshot2.jpg
│   │   │   │       ├── headshot3.jpg
│   │   │   │       ├── headshot4.jpg
│   │   │   │       ├── headshot5.jpg
│   │   │   │       └── headshot6.jpg
│   │   │   ├── index.html
│   │   │   └── js
│   │   │       ├── colorbox
│   │   │       │   ├── colorbox.min.css
│   │   │       │   ├── images
│   │   │       │   │   ├── border.png
│   │   │       │   │   ├── controls.png
│   │   │       │   │   ├── loading.gif
│   │   │       │   │   ├── loading_background.png
│   │   │       │   │   └── overlay.png
│   │   │       │   └── jquery.colorbox.min.js
│   │   │       ├── isotope
│   │   │       │   ├── imagesloaded.pkgd.min.js
│   │   │       │   └── jquery.isotope.min.js
│   │   │       ├── jquery-1.9.1.min.js
│   │   │       ├── navmaster
│   │   │       │   ├── jquery.nav.js
│   │   │       │   └── jquery.scrollTo.js
│   │   │       ├── script.js
│   │   │       └── waypoint
│   │   │           └── waypoints.min.js
│   │   ├── img
│   │   │   ├── Thumbs.db
│   │   │   ├── addressbook
│   │   │   │   ├── 1.jpg
│   │   │   │   ├── 2.jpg
│   │   │   │   ├── 3.jpg
│   │   │   │   ├── 4.jpg
│   │   │   │   └── 5.jpg
│   │   │   ├── avatars
│   │   │   │   ├── avatar1.jpg
│   │   │   │   ├── avatar2.jpg
│   │   │   │   ├── avatar3.jpg
│   │   │   │   ├── avatar4.jpg
│   │   │   │   ├── avatar5.jpg
│   │   │   │   ├── avatar6.jpg
│   │   │   │   ├── avatar7.jpg
│   │   │   │   └── avatar8.jpg
│   │   │   ├── carousel
│   │   │   │   ├── 1.jpg
│   │   │   │   ├── 2.jpg
│   │   │   │   └── 3.jpg
│   │   │   ├── chat
│   │   │   │   ├── headshot1.jpg
│   │   │   │   ├── headshot2.jpg
│   │   │   │   ├── headshot3.jpg
│   │   │   │   ├── headshot4.jpg
│   │   │   │   └── headshot5.jpg
│   │   │   ├── chat-arrow-mod.png
│   │   │   ├── chat-arrow.png
│   │   │   ├── dots.png
│   │   │   ├── gallery
│   │   │   │   ├── 1.png
│   │   │   │   ├── 2.jpg
│   │   │   │   ├── 3.png
│   │   │   │   ├── 4.png
│   │   │   │   ├── 5.png
│   │   │   │   ├── 7.jpg
│   │   │   │   ├── 8.png
│   │   │   │   └── img
│   │   │   │       └── 1.jpg
│   │   │   ├── gritter
│   │   │   │   ├── buy.png
│   │   │   │   ├── cloud.png
│   │   │   │   └── settings.png
│   │   │   ├── headshot.png
│   │   │   ├── icons
│   │   │   │   ├── mobilephonetower1.png
│   │   │   │   ├── mobilephonetower10.png
│   │   │   │   ├── mobilephonetower2.png
│   │   │   │   ├── mobilephonetower3.png
│   │   │   │   ├── mobilephonetower4.png
│   │   │   │   ├── mobilephonetower5.png
│   │   │   │   ├── mobilephonetower6.png
│   │   │   │   ├── mobilephonetower7.png
│   │   │   │   ├── mobilephonetower8.png
│   │   │   │   ├── mobilephonetower9.png
│   │   │   │   ├── wifi1.png
│   │   │   │   ├── wifi10.png
│   │   │   │   ├── wifi2.png
│   │   │   │   ├── wifi3.png
│   │   │   │   ├── wifi4.png
│   │   │   │   ├── wifi5.png
│   │   │   │   ├── wifi6.png
│   │   │   │   ├── wifi7.png
│   │   │   │   ├── wifi8.png
│   │   │   │   └── wifi9.png
│   │   │   ├── inbox
│   │   │   │   ├── 1.jpg
│   │   │   │   ├── 2.jpg
│   │   │   │   ├── 3.jpg
│   │   │   │   └── avatar.jpg
│   │   │   ├── light_noise_diagonal.png
│   │   │   ├── loaders
│   │   │   │   ├── 1.gif
│   │   │   │   ├── 10.gif
│   │   │   │   ├── 11.gif
│   │   │   │   ├── 12.gif
│   │   │   │   ├── 13.gif
│   │   │   │   ├── 14.gif
│   │   │   │   ├── 15.gif
│   │   │   │   ├── 16.gif
│   │   │   │   ├── 17.gif
│   │   │   │   ├── 18.gif
│   │   │   │   ├── 2.gif
│   │   │   │   ├── 3.gif
│   │   │   │   ├── 4.gif
│   │   │   │   ├── 5.gif
│   │   │   │   ├── 6.gif
│   │   │   │   ├── 7.gif
│   │   │   │   ├── 8.gif
│   │   │   │   ├── 9.gif
│   │   │   │   └── loading.gif
│   │   │   ├── lockscreen.png
│   │   │   ├── login
│   │   │   │   ├── 1.jpg
│   │   │   │   ├── 2.jpg
│   │   │   │   ├── 3.jpg
│   │   │   │   ├── 4.jpg
│   │   │   │   └── 5.jpg
│   │   │   ├── logo
│   │   │   │   ├── Cloud.psd
│   │   │   │   ├── cloud.png
│   │   │   │   ├── extra_logos
│   │   │   │   │   ├── login_logo.png
│   │   │   │   │   ├── logo.png
│   │   │   │   │   ├── logo1.png
│   │   │   │   │   └── logo_old.png
│   │   │   │   ├── login_logo.png
│   │   │   │   ├── logo-alt.png
│   │   │   │   ├── logo.png
│   │   │   │   ├── logo_template
│   │   │   │   │   └── logo.xcf
│   │   │   │   └── nocout.png
│   │   │   ├── marker
│   │   │   │   ├── icon1_small.png
│   │   │   │   ├── icon2_small.png
│   │   │   │   ├── icon3_small.png
│   │   │   │   ├── icon4_small.png
│   │   │   │   ├── marker1.png
│   │   │   │   ├── marker2.png
│   │   │   │   ├── marker3.png
│   │   │   │   ├── marker4.png
│   │   │   │   ├── marker5.png
│   │   │   │   ├── marker6.png
│   │   │   │   ├── master01.png
│   │   │   │   ├── master02.png
│   │   │   │   ├── master03.png
│   │   │   │   ├── slave01.png
│   │   │   │   ├── slave02.png
│   │   │   │   └── slave03.png
│   │   │   ├── nms_icons
│   │   │   │   ├── big
│   │   │   │   │   ├── circle_green.png
│   │   │   │   │   ├── circle_grey.png
│   │   │   │   │   ├── circle_orange.png
│   │   │   │   │   ├── circle_red.png
│   │   │   │   │   ├── circle_yellow.png
│   │   │   │   │   ├── help_circle_blue.png
│   │   │   │   │   └── minus_circle_green.png
│   │   │   │   ├── circle_green.png
│   │   │   │   ├── circle_grey.png
│   │   │   │   ├── circle_orange.png
│   │   │   │   ├── circle_red.png
│   │   │   │   ├── circle_yellow.png
│   │   │   │   ├── help_circle_blue.png
│   │   │   │   ├── medium
│   │   │   │   │   ├── circle_green.png
│   │   │   │   │   ├── circle_grey.png
│   │   │   │   │   ├── circle_orange.png
│   │   │   │   │   ├── circle_red.png
│   │   │   │   │   ├── circle_yellow.png
│   │   │   │   │   ├── help_circle_blue.png
│   │   │   │   │   └── minus_circle_green.png
│   │   │   │   ├── minus_circle_green.png
│   │   │   │   └── small
│   │   │   │       ├── circle_green.png
│   │   │   │       ├── circle_grey.png
│   │   │   │       ├── circle_orange.png
│   │   │   │       ├── circle_red.png
│   │   │   │       ├── circle_yellow.png
│   │   │   │       ├── help_circle_blue.png
│   │   │   │       └── minus_circle_green.png
│   │   │   ├── pattern.png
│   │   │   ├── profile
│   │   │   │   └── avatar.jpg
│   │   │   ├── search
│   │   │   │   └── sample.jpg
│   │   │   ├── search-icon.png
│   │   │   ├── severity
│   │   │   │   ├── status-0.png
│   │   │   │   ├── status-1.png
│   │   │   │   ├── status-3.png
│   │   │   │   ├── status-4.png
│   │   │   │   ├── status_old_icons
│   │   │   │   │   ├── status-0.png
│   │   │   │   │   ├── status-1.png
│   │   │   │   │   ├── status-2.png
│   │   │   │   │   ├── status-3.png
│   │   │   │   │   ├── status-4.png
│   │   │   │   │   ├── status-5.png
│   │   │   │   │   ├── status-6.png
│   │   │   │   │   └── status-7.png
│   │   │   │   └── sttaus-5.png
│   │   │   ├── sidebar-menu-arrow.png
│   │   │   └── slider
│   │   │       ├── handle.png
│   │   │       └── handlev.png
│   │   └── js
│   │       ├── ajax_csrf.js
│   │       ├── autosize
│   │       │   └── jquery.autosize.min.js
│   │       ├── backstretch
│   │       │   └── jquery.backstretch.min.js
│   │       ├── blueimp
│   │       │   ├── gallery
│   │       │   │   ├── blueimp-gallery.min.css
│   │       │   │   └── jquery.blueimp-gallery.min.js
│   │       │   ├── javascript-canvas-to-blob
│   │       │   │   └── canvas-to-blob.min.js
│   │       │   ├── javascript-loadimg
│   │       │   │   └── load-image.min.js
│   │       │   └── javascript-template
│   │       │       └── tmpl.min.js
│   │       ├── bootbox
│   │       │   └── bootbox.min.js
│   │       ├── bootstrap-daterangepicker
│   │       │   ├── daterangepicker-bs3.css
│   │       │   ├── daterangepicker.min.js
│   │       │   └── moment.min.js
│   │       ├── bootstrap-file-input
│   │       │   └── bootstrap-file-input.js
│   │       ├── bootstrap-fileupload
│   │       │   ├── bootstrap-fileupload.min.css
│   │       │   └── bootstrap-fileupload.min.js
│   │       ├── bootstrap-inputmask
│   │       │   └── bootstrap-inputmask.min.js
│   │       ├── bootstrap-onhover
│   │       │   └── twitter-bootstrap-hover-dropdown.min.js
│   │       ├── bootstrap-switch
│   │       │   ├── bootstrap-switch.min.css
│   │       │   └── bootstrap-switch.min.js
│   │       ├── bootstrap-wizard
│   │       │   ├── form-wizard.js
│   │       │   ├── form-wizard.min.js
│   │       │   ├── jquery.bootstrap.wizard.js
│   │       │   ├── jquery.bootstrap.wizard.min.js
│   │       │   └── wizard.css
│   │       ├── bootstrap-wysiwyg
│   │       │   ├── bootstrap-wysiwyg.min.js
│   │       │   └── jquery.hotkeys.min.js
│   │       ├── charts.js
│   │       ├── ckeditor
│   │       │   ├── adapters
│   │       │   │   └── jquery.js
│   │       │   ├── build-config.js
│   │       │   ├── ckeditor.js
│   │       │   ├── config.js
│   │       │   ├── contents.css
│   │       │   ├── lang
│   │       │   │   ├── af.js
│   │       │   │   ├── ar.js
│   │       │   │   ├── bg.js
│   │       │   │   ├── bn.js
│   │       │   │   ├── bs.js
│   │       │   │   ├── ca.js
│   │       │   │   ├── cs.js
│   │       │   │   ├── cy.js
│   │       │   │   ├── da.js
│   │       │   │   ├── de.js
│   │       │   │   ├── el.js
│   │       │   │   ├── en-au.js
│   │       │   │   ├── en-ca.js
│   │       │   │   ├── en-gb.js
│   │       │   │   ├── en.js
│   │       │   │   ├── eo.js
│   │       │   │   ├── es.js
│   │       │   │   ├── et.js
│   │       │   │   ├── eu.js
│   │       │   │   ├── fa.js
│   │       │   │   ├── fi.js
│   │       │   │   ├── fo.js
│   │       │   │   ├── fr-ca.js
│   │       │   │   ├── fr.js
│   │       │   │   ├── gl.js
│   │       │   │   ├── gu.js
│   │       │   │   ├── he.js
│   │       │   │   ├── hi.js
│   │       │   │   ├── hr.js
│   │       │   │   ├── hu.js
│   │       │   │   ├── id.js
│   │       │   │   ├── is.js
│   │       │   │   ├── it.js
│   │       │   │   ├── ja.js
│   │       │   │   ├── ka.js
│   │       │   │   ├── km.js
│   │       │   │   ├── ko.js
│   │       │   │   ├── ku.js
│   │       │   │   ├── lt.js
│   │       │   │   ├── lv.js
│   │       │   │   ├── mk.js
│   │       │   │   ├── mn.js
│   │       │   │   ├── ms.js
│   │       │   │   ├── nb.js
│   │       │   │   ├── nl.js
│   │       │   │   ├── no.js
│   │       │   │   ├── pl.js
│   │       │   │   ├── pt-br.js
│   │       │   │   ├── pt.js
│   │       │   │   ├── ro.js
│   │       │   │   ├── ru.js
│   │       │   │   ├── si.js
│   │       │   │   ├── sk.js
│   │       │   │   ├── sl.js
│   │       │   │   ├── sq.js
│   │       │   │   ├── sr-latn.js
│   │       │   │   ├── sr.js
│   │       │   │   ├── sv.js
│   │       │   │   ├── th.js
│   │       │   │   ├── tr.js
│   │       │   │   ├── ug.js
│   │       │   │   ├── uk.js
│   │       │   │   ├── vi.js
│   │       │   │   ├── zh-cn.js
│   │       │   │   └── zh.js
│   │       │   ├── plugins
│   │       │   │   ├── a11yhelp
│   │       │   │   │   └── dialogs
│   │       │   │   │       ├── a11yhelp.js
│   │       │   │   │       └── lang
│   │       │   │   │           ├── _translationstatus.txt
│   │       │   │   │           ├── ar.js
│   │       │   │   │           ├── bg.js
│   │       │   │   │           ├── ca.js
│   │       │   │   │           ├── cs.js
│   │       │   │   │           ├── cy.js
│   │       │   │   │           ├── da.js
│   │       │   │   │           ├── de.js
│   │       │   │   │           ├── el.js
│   │       │   │   │           ├── en.js
│   │       │   │   │           ├── eo.js
│   │       │   │   │           ├── es.js
│   │       │   │   │           ├── et.js
│   │       │   │   │           ├── fa.js
│   │       │   │   │           ├── fi.js
│   │       │   │   │           ├── fr-ca.js
│   │       │   │   │           ├── fr.js
│   │       │   │   │           ├── gl.js
│   │       │   │   │           ├── gu.js
│   │       │   │   │           ├── he.js
│   │       │   │   │           ├── hi.js
│   │       │   │   │           ├── hr.js
│   │       │   │   │           ├── hu.js
│   │       │   │   │           ├── id.js
│   │       │   │   │           ├── it.js
│   │       │   │   │           ├── ja.js
│   │       │   │   │           ├── km.js
│   │       │   │   │           ├── ku.js
│   │       │   │   │           ├── lt.js
│   │       │   │   │           ├── lv.js
│   │       │   │   │           ├── mk.js
│   │       │   │   │           ├── mn.js
│   │       │   │   │           ├── nb.js
│   │       │   │   │           ├── nl.js
│   │       │   │   │           ├── no.js
│   │       │   │   │           ├── pl.js
│   │       │   │   │           ├── pt-br.js
│   │       │   │   │           ├── pt.js
│   │       │   │   │           ├── ro.js
│   │       │   │   │           ├── ru.js
│   │       │   │   │           ├── si.js
│   │       │   │   │           ├── sk.js
│   │       │   │   │           ├── sl.js
│   │       │   │   │           ├── sq.js
│   │       │   │   │           ├── sr-latn.js
│   │       │   │   │           ├── sr.js
│   │       │   │   │           ├── sv.js
│   │       │   │   │           ├── th.js
│   │       │   │   │           ├── tr.js
│   │       │   │   │           ├── ug.js
│   │       │   │   │           ├── uk.js
│   │       │   │   │           ├── vi.js
│   │       │   │   │           └── zh-cn.js
│   │       │   │   ├── about
│   │       │   │   │   └── dialogs
│   │       │   │   │       ├── about.js
│   │       │   │   │       ├── hidpi
│   │       │   │   │       │   └── logo_ckeditor.png
│   │       │   │   │       └── logo_ckeditor.png
│   │       │   │   ├── clipboard
│   │       │   │   │   └── dialogs
│   │       │   │   │       └── paste.js
│   │       │   │   ├── colordialog
│   │       │   │   │   └── dialogs
│   │       │   │   │       └── colordialog.js
│   │       │   │   ├── dialog
│   │       │   │   │   └── dialogDefinition.js
│   │       │   │   ├── div
│   │       │   │   │   └── dialogs
│   │       │   │   │       └── div.js
│   │       │   │   ├── fakeobjects
│   │       │   │   │   └── images
│   │       │   │   │       └── spacer.gif
│   │       │   │   ├── find
│   │       │   │   │   └── dialogs
│   │       │   │   │       └── find.js
│   │       │   │   ├── flash
│   │       │   │   │   ├── dialogs
│   │       │   │   │   │   └── flash.js
│   │       │   │   │   └── images
│   │       │   │   │       └── placeholder.png
│   │       │   │   ├── forms
│   │       │   │   │   ├── dialogs
│   │       │   │   │   │   ├── button.js
│   │       │   │   │   │   ├── checkbox.js
│   │       │   │   │   │   ├── form.js
│   │       │   │   │   │   ├── hiddenfield.js
│   │       │   │   │   │   ├── radio.js
│   │       │   │   │   │   ├── select.js
│   │       │   │   │   │   ├── textarea.js
│   │       │   │   │   │   └── textfield.js
│   │       │   │   │   └── images
│   │       │   │   │       └── hiddenfield.gif
│   │       │   │   ├── icons.png
│   │       │   │   ├── icons_hidpi.png
│   │       │   │   ├── iframe
│   │       │   │   │   ├── dialogs
│   │       │   │   │   │   └── iframe.js
│   │       │   │   │   └── images
│   │       │   │   │       └── placeholder.png
│   │       │   │   ├── image
│   │       │   │   │   ├── dialogs
│   │       │   │   │   │   └── image.js
│   │       │   │   │   └── images
│   │       │   │   │       └── noimage.png
│   │       │   │   ├── link
│   │       │   │   │   ├── dialogs
│   │       │   │   │   │   ├── anchor.js
│   │       │   │   │   │   └── link.js
│   │       │   │   │   └── images
│   │       │   │   │       ├── anchor.png
│   │       │   │   │       └── hidpi
│   │       │   │   │           └── anchor.png
│   │       │   │   ├── liststyle
│   │       │   │   │   └── dialogs
│   │       │   │   │       └── liststyle.js
│   │       │   │   ├── magicline
│   │       │   │   │   └── images
│   │       │   │   │       ├── hidpi
│   │       │   │   │       │   └── icon.png
│   │       │   │   │       └── icon.png
│   │       │   │   ├── pagebreak
│   │       │   │   │   └── images
│   │       │   │   │       └── pagebreak.gif
│   │       │   │   ├── pastefromword
│   │       │   │   │   └── filter
│   │       │   │   │       └── default.js
│   │       │   │   ├── preview
│   │       │   │   │   └── preview.html
│   │       │   │   ├── scayt
│   │       │   │   │   ├── LICENSE.md
│   │       │   │   │   ├── README.md
│   │       │   │   │   └── dialogs
│   │       │   │   │       ├── options.js
│   │       │   │   │       └── toolbar.css
│   │       │   │   ├── showblocks
│   │       │   │   │   └── images
│   │       │   │   │       ├── block_address.png
│   │       │   │   │       ├── block_blockquote.png
│   │       │   │   │       ├── block_div.png
│   │       │   │   │       ├── block_h1.png
│   │       │   │   │       ├── block_h2.png
│   │       │   │   │       ├── block_h3.png
│   │       │   │   │       ├── block_h4.png
│   │       │   │   │       ├── block_h5.png
│   │       │   │   │       ├── block_h6.png
│   │       │   │   │       ├── block_p.png
│   │       │   │   │       └── block_pre.png
│   │       │   │   ├── smiley
│   │       │   │   │   ├── dialogs
│   │       │   │   │   │   └── smiley.js
│   │       │   │   │   └── images
│   │       │   │   │       ├── angel_smile.gif
│   │       │   │   │       ├── angry_smile.gif
│   │       │   │   │       ├── broken_heart.gif
│   │       │   │   │       ├── confused_smile.gif
│   │       │   │   │       ├── cry_smile.gif
│   │       │   │   │       ├── devil_smile.gif
│   │       │   │   │       ├── embaressed_smile.gif
│   │       │   │   │       ├── embarrassed_smile.gif
│   │       │   │   │       ├── envelope.gif
│   │       │   │   │       ├── heart.gif
│   │       │   │   │       ├── kiss.gif
│   │       │   │   │       ├── lightbulb.gif
│   │       │   │   │       ├── omg_smile.gif
│   │       │   │   │       ├── regular_smile.gif
│   │       │   │   │       ├── sad_smile.gif
│   │       │   │   │       ├── shades_smile.gif
│   │       │   │   │       ├── teeth_smile.gif
│   │       │   │   │       ├── thumbs_down.gif
│   │       │   │   │       ├── thumbs_up.gif
│   │       │   │   │       ├── tongue_smile.gif
│   │       │   │   │       ├── tounge_smile.gif
│   │       │   │   │       ├── whatchutalkingabout_smile.gif
│   │       │   │   │       └── wink_smile.gif
│   │       │   │   ├── specialchar
│   │       │   │   │   └── dialogs
│   │       │   │   │       ├── lang
│   │       │   │   │       │   ├── _translationstatus.txt
│   │       │   │   │       │   ├── ar.js
│   │       │   │   │       │   ├── bg.js
│   │       │   │   │       │   ├── ca.js
│   │       │   │   │       │   ├── cs.js
│   │       │   │   │       │   ├── cy.js
│   │       │   │   │       │   ├── de.js
│   │       │   │   │       │   ├── el.js
│   │       │   │   │       │   ├── en.js
│   │       │   │   │       │   ├── eo.js
│   │       │   │   │       │   ├── es.js
│   │       │   │   │       │   ├── et.js
│   │       │   │   │       │   ├── fa.js
│   │       │   │   │       │   ├── fi.js
│   │       │   │   │       │   ├── fr-ca.js
│   │       │   │   │       │   ├── fr.js
│   │       │   │   │       │   ├── gl.js
│   │       │   │   │       │   ├── he.js
│   │       │   │   │       │   ├── hr.js
│   │       │   │   │       │   ├── hu.js
│   │       │   │   │       │   ├── id.js
│   │       │   │   │       │   ├── it.js
│   │       │   │   │       │   ├── ja.js
│   │       │   │   │       │   ├── ku.js
│   │       │   │   │       │   ├── lv.js
│   │       │   │   │       │   ├── nb.js
│   │       │   │   │       │   ├── nl.js
│   │       │   │   │       │   ├── no.js
│   │       │   │   │       │   ├── pl.js
│   │       │   │   │       │   ├── pt-br.js
│   │       │   │   │       │   ├── pt.js
│   │       │   │   │       │   ├── ru.js
│   │       │   │   │       │   ├── si.js
│   │       │   │   │       │   ├── sk.js
│   │       │   │   │       │   ├── sl.js
│   │       │   │   │       │   ├── sq.js
│   │       │   │   │       │   ├── sv.js
│   │       │   │   │       │   ├── th.js
│   │       │   │   │       │   ├── tr.js
│   │       │   │   │       │   ├── ug.js
│   │       │   │   │       │   ├── uk.js
│   │       │   │   │       │   ├── vi.js
│   │       │   │   │       │   └── zh-cn.js
│   │       │   │   │       └── specialchar.js
│   │       │   │   ├── table
│   │       │   │   │   └── dialogs
│   │       │   │   │       └── table.js
│   │       │   │   ├── tabletools
│   │       │   │   │   └── dialogs
│   │       │   │   │       └── tableCell.js
│   │       │   │   ├── templates
│   │       │   │   │   ├── dialogs
│   │       │   │   │   │   ├── templates.css
│   │       │   │   │   │   └── templates.js
│   │       │   │   │   └── templates
│   │       │   │   │       ├── default.js
│   │       │   │   │       └── images
│   │       │   │   │           ├── template1.gif
│   │       │   │   │           ├── template2.gif
│   │       │   │   │           └── template3.gif
│   │       │   │   └── wsc
│   │       │   │       ├── LICENSE.md
│   │       │   │       ├── README.md
│   │       │   │       └── dialogs
│   │       │   │           ├── ciframe.html
│   │       │   │           ├── tmp.html
│   │       │   │           ├── tmpFrameset.html
│   │       │   │           ├── wsc.css
│   │       │   │           ├── wsc.js
│   │       │   │           └── wsc_ie.js
│   │       │   ├── skins
│   │       │   │   └── moono
│   │       │   │       ├── dialog.css
│   │       │   │       ├── dialog_ie.css
│   │       │   │       ├── dialog_ie7.css
│   │       │   │       ├── dialog_ie8.css
│   │       │   │       ├── dialog_iequirks.css
│   │       │   │       ├── dialog_opera.css
│   │       │   │       ├── editor.css
│   │       │   │       ├── editor_gecko.css
│   │       │   │       ├── editor_ie.css
│   │       │   │       ├── editor_ie7.css
│   │       │   │       ├── editor_ie8.css
│   │       │   │       ├── editor_iequirks.css
│   │       │   │       ├── icons.png
│   │       │   │       ├── icons_hidpi.png
│   │       │   │       ├── images
│   │       │   │       │   ├── arrow.png
│   │       │   │       │   ├── close.png
│   │       │   │       │   ├── hidpi
│   │       │   │       │   │   ├── close.png
│   │       │   │       │   │   ├── lock-open.png
│   │       │   │       │   │   ├── lock.png
│   │       │   │       │   │   └── refresh.png
│   │       │   │       │   ├── lock-open.png
│   │       │   │       │   ├── lock.png
│   │       │   │       │   └── refresh.png
│   │       │   │       └── readme.md
│   │       │   └── styles.js
│   │       ├── colorbox
│   │       │   ├── colorbox.min.css
│   │       │   ├── images
│   │       │   │   ├── border.png
│   │       │   │   ├── controls.png
│   │       │   │   ├── loading.gif
│   │       │   │   ├── loading_background.png
│   │       │   │   └── overlay.png
│   │       │   └── jquery.colorbox.min.js
│   │       ├── colorpicker
│   │       │   ├── css
│   │       │   │   └── colorpicker.min.css
│   │       │   ├── img
│   │       │   │   ├── alpha.png
│   │       │   │   ├── hue.png
│   │       │   │   └── saturation.png
│   │       │   └── js
│   │       │       └── bootstrap-colorpicker.min.js
│   │       ├── countable
│   │       │   └── jquery.simplyCountable.min.js
│   │       ├── d3
│   │       │   ├── d3.v3.js
│   │       │   └── d3.v3.min.js
│   │       ├── datatables
│   │       │   ├── extras
│   │       │   │   ├── AutoFill
│   │       │   │   │   ├── callbacks.html
│   │       │   │   │   ├── columns.html
│   │       │   │   │   ├── index.html
│   │       │   │   │   ├── inputs.html
│   │       │   │   │   ├── media
│   │       │   │   │   │   ├── css
│   │       │   │   │   │   │   └── AutoFill.css
│   │       │   │   │   │   ├── docs
│   │       │   │   │   │   │   ├── 02ff627f40.html
│   │       │   │   │   │   │   ├── 36456bf45f.html
│   │       │   │   │   │   │   ├── 47cac4f141.html
│   │       │   │   │   │   │   ├── 5a72546831.html
│   │       │   │   │   │   │   ├── 8ee4007a12.html
│   │       │   │   │   │   │   ├── AutoFill.html
│   │       │   │   │   │   │   ├── a69b02bcf2.html
│   │       │   │   │   │   │   ├── b44bd4821a.html
│   │       │   │   │   │   │   ├── c6945fdb4a.html
│   │       │   │   │   │   │   ├── global.html
│   │       │   │   │   │   │   ├── index.html
│   │       │   │   │   │   │   └── media
│   │       │   │   │   │   │       ├── css
│   │       │   │   │   │   │       │   ├── doc.css
│   │       │   │   │   │   │       │   ├── shCore.css
│   │       │   │   │   │   │       │   └── shThemeDataTables.css
│   │       │   │   │   │   │       ├── images
│   │       │   │   │   │   │       │   ├── arrow.jpg
│   │       │   │   │   │   │       │   ├── arrow.png
│   │       │   │   │   │   │       │   └── extended.png
│   │       │   │   │   │   │       ├── js
│   │       │   │   │   │   │       │   ├── doc.js
│   │       │   │   │   │   │       │   ├── jquery.js
│   │       │   │   │   │   │       │   ├── shBrushJScript.js
│   │       │   │   │   │   │       │   └── shCore.js
│   │       │   │   │   │   │       └── license
│   │       │   │   │   │   │           └── Syntax Highlighter
│   │       │   │   │   │   ├── images
│   │       │   │   │   │   │   └── filler.png
│   │       │   │   │   │   └── js
│   │       │   │   │   │       ├── AutoFill.js
│   │       │   │   │   │       ├── AutoFill.min.js
│   │       │   │   │   │       └── AutoFill.min.js.gz
│   │       │   │   │   └── scrolling.html
│   │       │   │   ├── ColReorder
│   │       │   │   │   ├── alt_insert.html
│   │       │   │   │   ├── col_filter.html
│   │       │   │   │   ├── colvis.html
│   │       │   │   │   ├── fixedcolumns.html
│   │       │   │   │   ├── fixedheader.html
│   │       │   │   │   ├── index.html
│   │       │   │   │   ├── media
│   │       │   │   │   │   ├── css
│   │       │   │   │   │   │   └── ColReorder.css
│   │       │   │   │   │   ├── docs
│   │       │   │   │   │   │   ├── 46848f6f3b.html
│   │       │   │   │   │   │   ├── 4f1246032c.html
│   │       │   │   │   │   │   ├── ColReorder.html
│   │       │   │   │   │   │   ├── a69b02bcf2.html
│   │       │   │   │   │   │   ├── global.html
│   │       │   │   │   │   │   ├── index.html
│   │       │   │   │   │   │   └── media
│   │       │   │   │   │   │       ├── css
│   │       │   │   │   │   │       │   ├── doc.css
│   │       │   │   │   │   │       │   ├── shCore.css
│   │       │   │   │   │   │       │   └── shThemeDataTables.css
│   │       │   │   │   │   │       ├── images
│   │       │   │   │   │   │       │   ├── arrow.jpg
│   │       │   │   │   │   │       │   ├── arrow.png
│   │       │   │   │   │   │       │   └── extended.png
│   │       │   │   │   │   │       ├── js
│   │       │   │   │   │   │       │   ├── doc.js
│   │       │   │   │   │   │       │   ├── jquery.js
│   │       │   │   │   │   │       │   ├── shBrushJScript.js
│   │       │   │   │   │   │       │   └── shCore.js
│   │       │   │   │   │   │       └── license
│   │       │   │   │   │   │           └── Syntax Highlighter
│   │       │   │   │   │   ├── images
│   │       │   │   │   │   │   └── insert.png
│   │       │   │   │   │   └── js
│   │       │   │   │   │       ├── ColReorder.js
│   │       │   │   │   │       ├── ColReorder.min.js
│   │       │   │   │   │       └── ColReorder.min.js.gz
│   │       │   │   │   ├── predefined.html
│   │       │   │   │   ├── reset.html
│   │       │   │   │   ├── scrolling.html
│   │       │   │   │   ├── server_side.html
│   │       │   │   │   ├── state_save.html
│   │       │   │   │   └── theme.html
│   │       │   │   ├── ColVis
│   │       │   │   │   ├── exclude_columns.html
│   │       │   │   │   ├── index.html
│   │       │   │   │   ├── media
│   │       │   │   │   │   ├── css
│   │       │   │   │   │   │   ├── ColVis.css
│   │       │   │   │   │   │   └── ColVisAlt.css
│   │       │   │   │   │   ├── docs
│   │       │   │   │   │   │   ├── ColVis.html
│   │       │   │   │   │   │   ├── a69b02bcf2.html
│   │       │   │   │   │   │   ├── ccb5a49865.html
│   │       │   │   │   │   │   ├── global.html
│   │       │   │   │   │   │   ├── index.html
│   │       │   │   │   │   │   └── media
│   │       │   │   │   │   │       ├── css
│   │       │   │   │   │   │       │   ├── doc.css
│   │       │   │   │   │   │       │   ├── shCore.css
│   │       │   │   │   │   │       │   └── shThemeDataTables.css
│   │       │   │   │   │   │       ├── images
│   │       │   │   │   │   │       │   ├── arrow.jpg
│   │       │   │   │   │   │       │   ├── arrow.png
│   │       │   │   │   │   │       │   └── extended.png
│   │       │   │   │   │   │       ├── js
│   │       │   │   │   │   │       │   ├── doc.js
│   │       │   │   │   │   │       │   ├── jquery.js
│   │       │   │   │   │   │       │   ├── shBrushJScript.js
│   │       │   │   │   │   │       │   └── shCore.js
│   │       │   │   │   │   │       └── license
│   │       │   │   │   │   │           └── Syntax Highlighter
│   │       │   │   │   │   ├── images
│   │       │   │   │   │   │   └── button.png
│   │       │   │   │   │   └── js
│   │       │   │   │   │       ├── ColVis.js
│   │       │   │   │   │       ├── ColVis.min.js
│   │       │   │   │   │       └── ColVis.min.js.gz
│   │       │   │   │   ├── mouseover.html
│   │       │   │   │   ├── style.html
│   │       │   │   │   ├── text.html
│   │       │   │   │   ├── theme.html
│   │       │   │   │   ├── title_callback.html
│   │       │   │   │   ├── two_tables.html
│   │       │   │   │   └── two_tables_identical.html
│   │       │   │   ├── FixedColumns
│   │       │   │   │   ├── col_filter.html
│   │       │   │   │   ├── css_size.html
│   │       │   │   │   ├── docs
│   │       │   │   │   │   ├── 070023b890.html
│   │       │   │   │   │   ├── 526f872207.html
│   │       │   │   │   │   ├── 73098af57c.html
│   │       │   │   │   │   ├── 889588ec06.html
│   │       │   │   │   │   ├── 91bce7c4ad.html
│   │       │   │   │   │   ├── FixedColumns.defaults.html
│   │       │   │   │   │   ├── FixedColumns.html
│   │       │   │   │   │   ├── a6bd52f587.html
│   │       │   │   │   │   ├── d3890ba7c4.html
│   │       │   │   │   │   ├── e20106c59a.html
│   │       │   │   │   │   ├── global.html
│   │       │   │   │   │   ├── index.html
│   │       │   │   │   │   └── media
│   │       │   │   │   │       ├── css
│   │       │   │   │   │       │   ├── doc.css
│   │       │   │   │   │       │   ├── shCore.css
│   │       │   │   │   │       │   └── shThemeDataTables.css
│   │       │   │   │   │       ├── images
│   │       │   │   │   │       │   ├── arrow.jpg
│   │       │   │   │   │       │   ├── arrow.png
│   │       │   │   │   │       │   └── extended.png
│   │       │   │   │   │       ├── js
│   │       │   │   │   │       │   ├── doc.js
│   │       │   │   │   │       │   ├── jquery.js
│   │       │   │   │   │       │   ├── shBrushJScript.js
│   │       │   │   │   │       │   └── shCore.js
│   │       │   │   │   │       └── license
│   │       │   │   │   │           └── Syntax Highlighter
│   │       │   │   │   ├── index.html
│   │       │   │   │   ├── index_column.html
│   │       │   │   │   ├── left_right_columns.html
│   │       │   │   │   ├── media
│   │       │   │   │   │   └── js
│   │       │   │   │   │       ├── FixedColumns.js
│   │       │   │   │   │       ├── FixedColumns.min.js
│   │       │   │   │   │       └── FixedColumns.min.js.gz
│   │       │   │   │   ├── right_column.html
│   │       │   │   │   ├── row_grouping.html
│   │       │   │   │   ├── row_grouping_height.html
│   │       │   │   │   ├── rowspan.html
│   │       │   │   │   ├── scale_fixed.html
│   │       │   │   │   ├── scale_relative.html
│   │       │   │   │   ├── server-side-processing.html
│   │       │   │   │   ├── themed.html
│   │       │   │   │   ├── two_columns.html
│   │       │   │   │   └── x_y_scrolling.html
│   │       │   │   ├── FixedHeader
│   │       │   │   │   ├── html_table.html
│   │       │   │   │   ├── index.html
│   │       │   │   │   ├── js
│   │       │   │   │   │   ├── FixedHeader.js
│   │       │   │   │   │   ├── FixedHeader.min.js
│   │       │   │   │   │   └── FixedHeader.min.js.gz
│   │       │   │   │   ├── top_bottom_left_right.html
│   │       │   │   │   ├── top_left.html
│   │       │   │   │   ├── two_tables.html
│   │       │   │   │   └── zIndexes.html
│   │       │   │   ├── KeyTable
│   │       │   │   │   ├── datatable.html
│   │       │   │   │   ├── datatable_scrolling.html
│   │       │   │   │   ├── editing.html
│   │       │   │   │   ├── form.html
│   │       │   │   │   ├── index.html
│   │       │   │   │   └── js
│   │       │   │   │       ├── KeyTable.js
│   │       │   │   │       ├── KeyTable.min.js
│   │       │   │   │       └── KeyTable.min.js.gz
│   │       │   │   ├── Scroller
│   │       │   │   │   ├── api_scrolling.html
│   │       │   │   │   ├── index.html
│   │       │   │   │   ├── large_js_source.html
│   │       │   │   │   ├── media
│   │       │   │   │   │   ├── css
│   │       │   │   │   │   │   └── dataTables.scroller.css
│   │       │   │   │   │   ├── data
│   │       │   │   │   │   │   ├── 2500.txt
│   │       │   │   │   │   │   └── server_processing.php
│   │       │   │   │   │   ├── docs
│   │       │   │   │   │   │   ├── Scroller.html
│   │       │   │   │   │   │   ├── Scroller.oDefaults.html
│   │       │   │   │   │   │   ├── baed189d4a.html
│   │       │   │   │   │   │   ├── c6053fac6b.html
│   │       │   │   │   │   │   ├── index.html
│   │       │   │   │   │   │   └── media
│   │       │   │   │   │   │       ├── css
│   │       │   │   │   │   │       │   ├── doc.css
│   │       │   │   │   │   │       │   ├── shCore.css
│   │       │   │   │   │   │       │   └── shThemeDataTables.css
│   │       │   │   │   │   │       ├── images
│   │       │   │   │   │   │       │   ├── arrow.jpg
│   │       │   │   │   │   │       │   ├── arrow.png
│   │       │   │   │   │   │       │   └── extended.png
│   │       │   │   │   │   │       ├── js
│   │       │   │   │   │   │       │   ├── doc.js
│   │       │   │   │   │   │       │   ├── jquery.js
│   │       │   │   │   │   │       │   ├── shBrushJScript.js
│   │       │   │   │   │   │       │   └── shCore.js
│   │       │   │   │   │   │       └── license
│   │       │   │   │   │   │           └── Syntax Highlighter
│   │       │   │   │   │   ├── images
│   │       │   │   │   │   │   └── loading-background.png
│   │       │   │   │   │   └── js
│   │       │   │   │   │       ├── dataTables.scroller.js
│   │       │   │   │   │       ├── dataTables.scroller.min.js
│   │       │   │   │   │       └── dataTables.scroller.min.js.gz
│   │       │   │   │   ├── server-side_processing.html
│   │       │   │   │   └── state_saving.html
│   │       │   │   └── TableTools
│   │       │   │       ├── alt_init.html
│   │       │   │       ├── alter_buttons.html
│   │       │   │       ├── bootstrap.html
│   │       │   │       ├── button_text.html
│   │       │   │       ├── collection.html
│   │       │   │       ├── defaults.html
│   │       │   │       ├── index.html
│   │       │   │       ├── media
│   │       │   │       │   ├── as3
│   │       │   │       │   │   ├── ZeroClipboard.as
│   │       │   │       │   │   ├── ZeroClipboardPdf.as
│   │       │   │       │   │   └── lib
│   │       │   │       │   │       └── AlivePDF.swc
│   │       │   │       │   ├── css
│   │       │   │       │   │   ├── TableTools.min.css
│   │       │   │       │   │   └── TableTools_JUI.css
│   │       │   │       │   ├── images
│   │       │   │       │   │   ├── background.png
│   │       │   │       │   │   ├── collection.png
│   │       │   │       │   │   ├── collection_hover.png
│   │       │   │       │   │   ├── copy.png
│   │       │   │       │   │   ├── copy_hover.png
│   │       │   │       │   │   ├── csv.png
│   │       │   │       │   │   ├── csv_hover.png
│   │       │   │       │   │   ├── pdf.png
│   │       │   │       │   │   ├── pdf_hover.png
│   │       │   │       │   │   ├── print.png
│   │       │   │       │   │   ├── print_hover.png
│   │       │   │       │   │   ├── psd
│   │       │   │       │   │   │   ├── collection.psd
│   │       │   │       │   │   │   ├── copy document.psd
│   │       │   │       │   │   │   ├── file_types.psd
│   │       │   │       │   │   │   └── printer.psd
│   │       │   │       │   │   ├── xls.png
│   │       │   │       │   │   └── xls_hover.png
│   │       │   │       │   ├── js
│   │       │   │       │   │   ├── TableTools.min.js
│   │       │   │       │   │   ├── TableTools.min.js.gz
│   │       │   │       │   │   └── ZeroClipboard.min.js
│   │       │   │       │   └── swf
│   │       │   │       │       ├── copy_csv_xls.swf
│   │       │   │       │       └── copy_csv_xls_pdf.swf
│   │       │   │       ├── multi_instance.html
│   │       │   │       ├── multiple_tables.html
│   │       │   │       ├── pdf_message.html
│   │       │   │       ├── plug-in.html
│   │       │   │       ├── select_multi.html
│   │       │   │       ├── select_single.html
│   │       │   │       ├── swf_path.html
│   │       │   │       ├── tabs.html
│   │       │   │       └── theme.html
│   │       │   └── media
│   │       │       ├── assets
│   │       │       │   ├── css
│   │       │       │   │   └── datatables.min.css
│   │       │       │   ├── images
│   │       │       │   │   ├── sort_asc.png
│   │       │       │   │   ├── sort_asc_disabled.png
│   │       │       │   │   ├── sort_both.png
│   │       │       │   │   ├── sort_desc.png
│   │       │       │   │   └── sort_desc_disabled.png
│   │       │       │   └── js
│   │       │       │       └── datatables.min.js
│   │       │       ├── css
│   │       │       │   ├── demo_page.css
│   │       │       │   ├── demo_table.css
│   │       │       │   ├── demo_table_jui.css
│   │       │       │   ├── jquery.dataTables.min.css
│   │       │       │   └── jquery.dataTables_themeroller.css
│   │       │       ├── images
│   │       │       │   ├── Sorting icons.psd
│   │       │       │   ├── back_disabled.png
│   │       │       │   ├── back_enabled.png
│   │       │       │   ├── back_enabled_hover.png
│   │       │       │   ├── favicon.ico
│   │       │       │   ├── forward_disabled.png
│   │       │       │   ├── forward_enabled.png
│   │       │       │   ├── forward_enabled_hover.png
│   │       │       │   ├── sort_asc.png
│   │       │       │   ├── sort_asc_disabled.png
│   │       │       │   ├── sort_both.png
│   │       │       │   ├── sort_desc.png
│   │       │       │   └── sort_desc_disabled.png
│   │       │       └── js
│   │       │           ├── jquery.dataTables.js
│   │       │           ├── jquery.dataTables.min.js
│   │       │           └── jquery.js
│   │       ├── datepicker
│   │       │   ├── legacy.js
│   │       │   ├── picker.date.js
│   │       │   ├── picker.js
│   │       │   ├── picker.time.js
│   │       │   └── themes
│   │       │       ├── default.date.min.css
│   │       │       ├── default.min.css
│   │       │       └── default.time.min.css
│   │       ├── dropzone
│   │       │   ├── dropzone.min.css
│   │       │   ├── dropzone.min.js
│   │       │   ├── spritemap.png
│   │       │   └── spritemap@2x.png
│   │       ├── easypiechart
│   │       │   ├── angular.easypiechart.min.js
│   │       │   ├── easypiechart.min.js
│   │       │   ├── jquery.easypiechart.min.js
│   │       │   ├── jquery.easypiechart.min.js.2.0
│   │       │   └── jquery.easypiechart.min.js.older
│   │       ├── flot
│   │       │   ├── excanvas.min.js
│   │       │   ├── jquery.colorhelpers.min.js
│   │       │   ├── jquery.flot.canvas.min.js
│   │       │   ├── jquery.flot.categories.min.js
│   │       │   ├── jquery.flot.crosshair.min.js
│   │       │   ├── jquery.flot.errorbars.min.js
│   │       │   ├── jquery.flot.fillbetween.min.js
│   │       │   ├── jquery.flot.image.min.js
│   │       │   ├── jquery.flot.min.js
│   │       │   ├── jquery.flot.navigate.min.js
│   │       │   ├── jquery.flot.pie.min.js
│   │       │   ├── jquery.flot.resize.min.js
│   │       │   ├── jquery.flot.selection.min.js
│   │       │   ├── jquery.flot.stack.min.js
│   │       │   ├── jquery.flot.symbol.min.js
│   │       │   ├── jquery.flot.threshold.min.js
│   │       │   ├── jquery.flot.time.min.js
│   │       │   └── jquery.min.js
│   │       ├── flot-growraf
│   │       │   └── jquery.flot.growraf.min.js
│   │       ├── fuelux-tree
│   │       │   ├── fuelux-responsive.min.css
│   │       │   ├── fuelux.min.css
│   │       │   ├── fuelux.tree-sampledata.js
│   │       │   ├── fuelux.tree.min.js
│   │       │   └── tree.min.js
│   │       ├── fullcalendar
│   │       │   ├── fullcalendar.min.css
│   │       │   ├── fullcalendar.min.js
│   │       │   ├── fullcalendar.print.css
│   │       │   └── gcal.js
│   │       ├── gmaps
│   │       │   └── gmaps.min.js
│   │       ├── googlemaps.js
│   │       ├── gritter
│   │       │   ├── css
│   │       │   │   └── jquery.gritter.css
│   │       │   ├── images
│   │       │   │   ├── gritter-light.png
│   │       │   │   ├── gritter-long.png
│   │       │   │   ├── gritter.png
│   │       │   │   └── ie-spacer.gif
│   │       │   └── js
│   │       │       └── jquery.gritter.min.js
│   │       ├── highchartstable.js
│   │       ├── highcharttheme.js
│   │       ├── html5
│   │       │   └── html5.js
│   │       ├── hubspot-messenger
│   │       │   ├── css
│   │       │   │   ├── messenger-spinner.min.css
│   │       │   │   ├── messenger-theme-air.min.css
│   │       │   │   ├── messenger-theme-block.min.css
│   │       │   │   ├── messenger-theme-flat.min.css
│   │       │   │   ├── messenger-theme-future.min.css
│   │       │   │   ├── messenger-theme-ice.min.css
│   │       │   │   └── messenger.min.css
│   │       │   └── js
│   │       │       ├── messenger-theme-flat.js
│   │       │       ├── messenger-theme-future.js
│   │       │       └── messenger.min.js
│   │       ├── inbox.js
│   │       ├── isotope
│   │       │   ├── imagesloaded.pkgd.min.js
│   │       │   └── jquery.isotope.min.js
│   │       ├── jQuery-BlockUI
│   │       │   └── jquery.blockUI.min.js
│   │       ├── jQuery-Cookie
│   │       │   └── jquery.cookie.min.js
│   │       ├── jQuery-Knob
│   │       │   ├── js
│   │       │   │   └── jquery.knob.min.js
│   │       │   └── knob.jquery.json
│   │       ├── jQuery-slimScroll-1.3.0
│   │       │   ├── jquery.slimscroll.min.js
│   │       │   └── slimScrollHorizontal.min.js
│   │       ├── jqgrid
│   │       │   ├── css
│   │       │   │   └── ui.jqgrid.min.css
│   │       │   └── js
│   │       │       ├── grid.locale-en.min.js
│   │       │       └── jquery.jqGrid.min.js
│   │       ├── jquery
│   │       │   ├── jquery-1.11.1.min.js
│   │       │   ├── jquery-2.0.3.min.js
│   │       │   └── jquery-migrate-1.2.1.min.js
│   │       ├── jquery-easing
│   │       │   └── jquery.easing.min.js
│   │       ├── jquery-raty
│   │       │   ├── img
│   │       │   │   ├── 0.png
│   │       │   │   ├── 1.png
│   │       │   │   ├── 2.png
│   │       │   │   ├── 3.png
│   │       │   │   ├── 4.png
│   │       │   │   ├── 5.png
│   │       │   │   ├── cancel-custom-off.png
│   │       │   │   ├── cancel-custom-on.png
│   │       │   │   ├── cancel-off-big.png
│   │       │   │   ├── cancel-off.png
│   │       │   │   ├── cancel-on-big.png
│   │       │   │   ├── cancel-on.png
│   │       │   │   ├── cookie-half.png
│   │       │   │   ├── cookie-off.png
│   │       │   │   ├── cookie-on.png
│   │       │   │   ├── off.png
│   │       │   │   ├── on.png
│   │       │   │   ├── star-half-big.png
│   │       │   │   ├── star-half.png
│   │       │   │   ├── star-off-big.png
│   │       │   │   ├── star-off.png
│   │       │   │   ├── star-on-big.png
│   │       │   │   └── star-on.png
│   │       │   └── jquery.raty.min.js
│   │       ├── jquery-todo
│   │       │   ├── css
│   │       │   │   └── styles.css
│   │       │   └── js
│   │       │       └── paddystodolist.js
│   │       ├── jquery-ui-1.10.3.custom
│   │       │   ├── css
│   │       │   │   └── custom-theme
│   │       │   │       ├── images
│   │       │   │       │   ├── animated-overlay.gif
│   │       │   │       │   ├── ui-bg_diagonals-thick_75_f3d8d8_40x40.png
│   │       │   │       │   ├── ui-bg_dots-small_65_a6a6a6_2x2.png
│   │       │   │       │   ├── ui-bg_flat_0_333333_40x100.png
│   │       │   │       │   ├── ui-bg_flat_100_eeeeee_40x100.png
│   │       │   │       │   ├── ui-bg_flat_100_f6f6f6_40x100.png
│   │       │   │       │   ├── ui-bg_flat_15_5E87B0_40x100.png
│   │       │   │       │   ├── ui-bg_flat_55_fbf8ee_40x100.png
│   │       │   │       │   ├── ui-bg_flat_65_ffffff_40x100.png
│   │       │   │       │   ├── ui-bg_flat_75_ffffff_40x100.png
│   │       │   │       │   ├── ui-icons_004276_256x240.png
│   │       │   │       │   ├── ui-icons_333333_256x240.png
│   │       │   │       │   ├── ui-icons_555555_256x240.png
│   │       │   │       │   ├── ui-icons_5E87B0_256x240.png
│   │       │   │       │   ├── ui-icons_cc0000_256x240.png
│   │       │   │       │   └── ui-icons_ffffff_256x240.png
│   │       │   │       └── jquery-ui-1.10.3.custom.min.css
│   │       │   └── js
│   │       │       ├── jquery-1.9.1.js
│   │       │       └── jquery-ui-1.10.3.custom.min.js
│   │       ├── jquery-upload
│   │       │   ├── css
│   │       │   │   ├── demo-ie8.css
│   │       │   │   ├── demo.css
│   │       │   │   ├── jquery.fileupload-noscript.css
│   │       │   │   ├── jquery.fileupload-ui-noscript.css
│   │       │   │   ├── jquery.fileupload-ui.css
│   │       │   │   ├── jquery.fileupload.css
│   │       │   │   └── style.css
│   │       │   ├── img
│   │       │   │   ├── loading.gif
│   │       │   │   └── progressbar.gif
│   │       │   └── js
│   │       │       ├── app.js
│   │       │       ├── cors
│   │       │       │   ├── jquery.postmessage-transport.js
│   │       │       │   └── jquery.xdr-transport.js
│   │       │       ├── jquery.fileupload-angular.js
│   │       │       ├── jquery.fileupload-audio.min.js
│   │       │       ├── jquery.fileupload-image.min.js
│   │       │       ├── jquery.fileupload-jquery-ui.js
│   │       │       ├── jquery.fileupload-process.min.js
│   │       │       ├── jquery.fileupload-ui.min.js
│   │       │       ├── jquery.fileupload-validate.min.js
│   │       │       ├── jquery.fileupload-video.min.js
│   │       │       ├── jquery.fileupload.min.js
│   │       │       ├── jquery.iframe-transport.js
│   │       │       ├── main.js
│   │       │       └── vendor
│   │       │           └── jquery.ui.widget.js
│   │       ├── jquery-validate
│   │       │   ├── additional-methods.js
│   │       │   ├── additional-methods.min.js
│   │       │   ├── jquery.validate.js
│   │       │   └── jquery.validate.min.js
│   │       ├── jqvmap
│   │       │   ├── data
│   │       │   │   └── jquery.vmap.sampledata.js
│   │       │   ├── jquery.vmap.min.js
│   │       │   ├── jquery.vmap.packed.js
│   │       │   ├── jqvmap.css
│   │       │   └── maps
│   │       │       ├── continents
│   │       │       │   ├── jquery.vmap.africa.js
│   │       │       │   ├── jquery.vmap.asia.js
│   │       │       │   ├── jquery.vmap.australia.js
│   │       │       │   ├── jquery.vmap.europe.js
│   │       │       │   ├── jquery.vmap.north-america.js
│   │       │       │   ├── jquery.vmap.south-america.js
│   │       │       │   └── readme.txt
│   │       │       ├── jquery.vmap.algeria.js
│   │       │       ├── jquery.vmap.europe.js
│   │       │       ├── jquery.vmap.france.js
│   │       │       ├── jquery.vmap.germany.js
│   │       │       ├── jquery.vmap.russia.js
│   │       │       ├── jquery.vmap.usa.js
│   │       │       └── jquery.vmap.world.js
│   │       ├── justgage
│   │       │   └── js
│   │       │       ├── justgage.1.0.1.js
│   │       │       ├── justgage.1.0.1.min.js
│   │       │       └── raphael.2.1.0.min.js
│   │       ├── magic-suggest
│   │       │   ├── magicsuggest-1.3.1-min.css
│   │       │   └── magicsuggest-1.3.1-min.js
│   │       ├── media-ie
│   │       │   └── css3-mediaqueries.js
│   │       ├── navmaster
│   │       │   ├── jquery.nav.js
│   │       │   └── jquery.scrollTo.js
│   │       ├── nestable
│   │       │   └── jquery.nestable.min.js
│   │       ├── nocout
│   │       │   ├── dummy_data
│   │       │   │   └── devices_list.js
│   │       │   ├── nocoutPerfLib.js
│   │       │   ├── nocoutSpinnerLib.js
│   │       │   ├── nocout_forms.js
│   │       │   ├── openTabContentLib.js
│   │       │   ├── selected_side_menu.js
│   │       │   └── softDeleteLib.js
│   │       ├── prettify
│   │       │   ├── prettify.css
│   │       │   └── prettify.js
│   │       ├── purl.js
│   │       ├── script.js
│   │       ├── select2
│   │       │   ├── select2-spinner.gif
│   │       │   ├── select2.min.css
│   │       │   ├── select2.min.js
│   │       │   ├── select2.png
│   │       │   └── select2x2.png
│   │       ├── slidernav
│   │       │   ├── slidernav.css
│   │       │   └── slidernav.js
│   │       ├── sparklines
│   │       │   └── jquery.sparkline.min.js
│   │       ├── spin
│   │       │   └── spin.js
│   │       ├── tablecloth
│   │       │   ├── css
│   │       │   │   ├── bootstrap-responsive.css
│   │       │   │   ├── bootstrap-responsive.min.css
│   │       │   │   ├── bootstrap-tables.css
│   │       │   │   ├── bootstrap.css
│   │       │   │   ├── bootstrap.min.css
│   │       │   │   ├── prettify.css
│   │       │   │   └── tablecloth.min.css
│   │       │   ├── img
│   │       │   │   ├── asc.gif
│   │       │   │   ├── asc_light.gif
│   │       │   │   ├── desc.gif
│   │       │   │   ├── desc_light.gif
│   │       │   │   ├── glyphicons-halflings-white.png
│   │       │   │   └── glyphicons-halflings.png
│   │       │   └── js
│   │       │       ├── bootstrap.js
│   │       │       ├── bootstrap.min.js
│   │       │       ├── jquery-1.7.2.min.js
│   │       │       ├── jquery.metadata.js
│   │       │       ├── jquery.tablecloth.js
│   │       │       ├── jquery.tablesorter.js
│   │       │       └── jquery.tablesorter.min.js
│   │       ├── timeago
│   │       │   └── jquery.timeago.min.js
│   │       ├── timelinejs
│   │       │   ├── css
│   │       │   │   ├── blank.gif
│   │       │   │   ├── fancybox_sprite.png
│   │       │   │   ├── fancybox_sprite@2x.png
│   │       │   │   ├── loading.gif
│   │       │   │   ├── themes
│   │       │   │   │   ├── dark.css
│   │       │   │   │   ├── font
│   │       │   │   │   │   ├── AbrilFatface-Average.css
│   │       │   │   │   │   ├── Arvo-PTSans.css
│   │       │   │   │   │   ├── Bevan-PotanoSans.css
│   │       │   │   │   │   ├── BreeSerif-OpenSans.css
│   │       │   │   │   │   ├── DroidSerif-DroidSans.css
│   │       │   │   │   │   ├── Georgia-Helvetica.css
│   │       │   │   │   │   ├── Lekton-Molengo.css
│   │       │   │   │   │   ├── Lora-Istok.css
│   │       │   │   │   │   ├── Merriweather-NewsCycle.css
│   │       │   │   │   │   ├── NewsCycle-Merriweather.css
│   │       │   │   │   │   ├── NixieOne-Ledger.css
│   │       │   │   │   │   ├── PT.css
│   │       │   │   │   │   ├── PTSerif-PTSans.css
│   │       │   │   │   │   ├── Pacifico-Arimo.css
│   │       │   │   │   │   ├── PlayfairDisplay-Muli.css
│   │       │   │   │   │   ├── PoiretOne-Molengo.css
│   │       │   │   │   │   ├── Rancho-Gudea.css
│   │       │   │   │   │   └── SansitaOne-Kameron.css
│   │       │   │   │   ├── timeline-dark.png
│   │       │   │   │   ├── timeline-dark@2x.png
│   │       │   │   │   └── timeline-texture.png
│   │       │   │   ├── timeline.css
│   │       │   │   ├── timeline.png
│   │       │   │   └── timeline@2x.png
│   │       │   ├── embed
│   │       │   │   └── index.html
│   │       │   ├── example_json.json
│   │       │   └── js
│   │       │       ├── locale
│   │       │       │   ├── af.js
│   │       │       │   ├── ar.js
│   │       │       │   ├── bg.js
│   │       │       │   ├── ca.js
│   │       │       │   ├── cz.js
│   │       │       │   ├── da.js
│   │       │       │   ├── de.js
│   │       │       │   ├── el.js
│   │       │       │   ├── en-24hr.js
│   │       │       │   ├── en.js
│   │       │       │   ├── es.js
│   │       │       │   ├── eu.js
│   │       │       │   ├── fi.js
│   │       │       │   ├── fo.js
│   │       │       │   ├── fr.js
│   │       │       │   ├── gl.js
│   │       │       │   ├── he.js
│   │       │       │   ├── hu.js
│   │       │       │   ├── hy.js
│   │       │       │   ├── id.js
│   │       │       │   ├── is.js
│   │       │       │   ├── it.js
│   │       │       │   ├── iw.js
│   │       │       │   ├── ja.js
│   │       │       │   ├── ka.js
│   │       │       │   ├── ko.js
│   │       │       │   ├── lb.js
│   │       │       │   ├── lv.js
│   │       │       │   ├── nl.js
│   │       │       │   ├── no.js
│   │       │       │   ├── pl.js
│   │       │       │   ├── pt-br.js
│   │       │       │   ├── pt.js
│   │       │       │   ├── ru.js
│   │       │       │   ├── si.js
│   │       │       │   ├── sk.js
│   │       │       │   ├── sl.js
│   │       │       │   ├── sr-cy.js
│   │       │       │   ├── sr.js
│   │       │       │   ├── sv.js
│   │       │       │   ├── ta.js
│   │       │       │   ├── tl.js
│   │       │       │   ├── tr.js
│   │       │       │   ├── zh-cn.js
│   │       │       │   └── zh-tw.js
│   │       │       ├── storyjs-embed-cdn.js
│   │       │       ├── storyjs-embed-generator.js
│   │       │       ├── storyjs-embed.min.js
│   │       │       ├── timeline-min.js
│   │       │       └── timeline.js
│   │       ├── typeahead
│   │       │   ├── typeahead.css
│   │       │   └── typeahead.min.js
│   │       ├── uniform
│   │       │   ├── css
│   │       │   │   └── uniform.default.min.css
│   │       │   ├── images
│   │       │   │   ├── bg-input-focus.png
│   │       │   │   ├── bg-input.png
│   │       │   │   └── sprite.png
│   │       │   └── jquery.uniform.min.js
│   │       ├── utils
│   │       │   └── jqueryDataTable.js
│   │       ├── vertical-timeline
│   │       │   ├── css
│   │       │   │   └── style.css
│   │       │   ├── img
│   │       │   │   ├── button-up-down-arrow.png
│   │       │   │   ├── tab-left.png
│   │       │   │   └── tab-right.png
│   │       │   └── js
│   │       │       ├── handlebars.js
│   │       │       ├── libs
│   │       │       │   └── modernizr-2.5.3.min.js
│   │       │       ├── plugins.js
│   │       │       ├── script.js
│   │       │       └── tabletop.js
│   │       └── xcharts
│   │           ├── LICENSE
│   │           ├── README.md
│   │           ├── xcharts.css
│   │           ├── xcharts.js
│   │           ├── xcharts.min.css
│   │           └── xcharts.min.js
│   ├── templates
│   │   └── nocout
│   │       ├── base.html
│   │       ├── header.html
│   │       ├── invalid_login.html
│   │       ├── loggedin.html
│   │       ├── login.html
│   │       ├── logout.html
│   │       ├── mainpage.html
│   │       └── sidemenu.html
│   ├── urls.py
│   ├── utils
│   │   ├── __init__.py
│   │   ├── jquery_datatable_generation.py
│   │   └── util.py
│   ├── uwsgi_params
│   ├── views.py
│   ├── widgets.py
│   └── wsgi.py
├── nocout_main.log
├── organization
│   ├── __init__.py
│   ├── forms.py
│   ├── migrations
│   │   ├── 0001_initial.py
│   │   └── __init__.py
│   ├── models.py
│   ├── static
│   │   └── css
│   │       └── organization.css
│   ├── templates
│   │   └── organization
│   │       ├── organization.html
│   │       ├── organization_delete.html
│   │       ├── organization_detail.html
│   │       ├── organization_list.html
│   │       ├── organization_new.html
│   │       └── organization_update.html
│   ├── tests.py
│   ├── urls.py
│   └── views.py
├── performance
│   ├── __init__.py
│   ├── admin.py
│   ├── migrations
│   │   ├── 0001_initial.py
│   │   ├── 0002_auto__add_index_eventstatus_service_name__add_index_eventstatus_device.py
│   │   ├── 0003_auto__add_field_eventnetwork_description.py
│   │   ├── 0004_auto__chg_field_eventstatus_sys_timestamp__del_index_eventstatus_sys_t.py
│   │   └── __init__.py
│   ├── models.py
│   ├── templates
│   │   └── performance
│   │       ├── live_perf.html
│   │       ├── network_perf.html
│   │       ├── other_perf.html
│   │       ├── perf_dashboard.html
│   │       ├── sector_dashboard.html
│   │       └── single_device_perf.html
│   ├── tests.py
│   ├── urls.py
│   └── views.py
├── scheduling_management
│   ├── __init__.py
│   ├── admin.py
│   ├── models.py
│   ├── static
│   │   └── js
│   │       └── nocout_scheduling.js
│   ├── templates
│   │   └── scheduling_management
│   │       └── scheduler_template.html
│   ├── tests.py
│   ├── urls.py
│   └── views.py
├── schema
│   ├── db_dummy_data
│   │   └── nocout_dev - dummy data.sql
│   ├── db_dump
│   │   └── nocout_dev.sql
│   └── initial_data_sql
│       └── initial_data_v1.sql
├── service
│   ├── __init__.py
│   ├── device_service_configuration_urls.py
│   ├── forms.py
│   ├── migrations
│   │   ├── 0001_initial.py
│   │   ├── 0002_auto__add_field_deviceserviceconfiguration_is_added.py
│   │   └── __init__.py
│   ├── models.py
│   ├── para_urls.py
│   ├── protocol_urls.py
│   ├── service_data_source_urls.py
│   ├── static
│   │   ├── css
│   │   │   └── service.css
│   │   └── js
│   │       └── service.js
│   ├── templates
│   │   ├── device_service_configuration
│   │   │   └── device_service_configuration_list.html
│   │   ├── protocol
│   │   │   ├── protocol_delete.html
│   │   │   ├── protocol_detail.html
│   │   │   ├── protocol_new.html
│   │   │   ├── protocol_update.html
│   │   │   └── protocols_list.html
│   │   ├── service
│   │   │   ├── service_delete.html
│   │   │   ├── service_detail.html
│   │   │   ├── service_new.html
│   │   │   ├── service_update.html
│   │   │   └── services_list.html
│   │   ├── service_data_source
│   │   │   ├── service_data_source_delete.html
│   │   │   ├── service_data_source_detail.html
│   │   │   ├── service_data_source_new.html
│   │   │   ├── service_data_source_update.html
│   │   │   └── service_data_sources_list.html
│   │   └── service_parameter
│   │       ├── service_parameter_delete.html
│   │       ├── service_parameter_detail.html
│   │       ├── service_parameter_new.html
│   │       ├── service_parameter_update.html
│   │       └── services_parameter_list.html
│   ├── tests.py
│   ├── urls.py
│   └── views.py
├── service_group
│   ├── __init__.py
│   ├── models.py
│   ├── tests.py
│   └── views.py
├── session_management
│   ├── __init__.py
│   ├── models.py
│   ├── static
│   │   └── session_management
│   │       └── img
│   │           ├── icon-False.gif
│   │           └── icon-True.gif
│   ├── templates
│   │   └── session_management
│   │       └── users_status_list.html
│   ├── urls.py
│   └── views.py
├── session_security
│   ├── __init__.py
│   ├── locale
│   │   ├── fr
│   │   │   └── LC_MESSAGES
│   │   │       ├── django.mo
│   │   │       └── django.po
│   │   └── pt_BR
│   │       └── LC_MESSAGES
│   │           ├── django.mo
│   │           └── django.po
│   ├── middleware.py
│   ├── models.py
│   ├── settings.py
│   ├── static
│   │   └── session_security
│   │       ├── script.js
│   │       └── style.css
│   ├── templates
│   │   └── session_security
│   │       ├── all.html
│   │       └── dialog.html
│   ├── templatetags
│   │   ├── __init__.py
│   │   └── session_security_tags.py
│   ├── tests
│   │   ├── __init__.py
│   │   ├── base.py
│   │   ├── middleware.py
│   │   ├── script.py
│   │   └── views.py
│   ├── urls.py
│   ├── utils.py
│   └── views.py
├── site_instance
│   ├── __init__.py
│   ├── admin.py
│   ├── forms.py
│   ├── migrations
│   │   ├── 0001_initial.py
│   │   └── __init__.py
│   ├── models.py
│   ├── static
│   │   └── css
│   │       └── site_instance.css
│   ├── templates
│   │   └── site_instance
│   │       ├── site_instance_delete.html
│   │       ├── site_instance_detail.html
│   │       ├── site_instance_list.html
│   │       ├── site_instance_new.html
│   │       └── site_instance_update.html
│   ├── tests.py
│   ├── urls.py
│   └── views.py
├── sitesearch
│   ├── __init__.py
│   ├── admin.py
│   ├── models.py
│   ├── tests.py
│   ├── urls.py
│   └── views.py
├── static
├── user_group
│   ├── __init__.py
│   ├── admin.py
│   ├── ajax.py
│   ├── forms.py
│   ├── migrations
│   │   ├── 0001_initial.py
│   │   └── __init__.py
│   ├── models.py
│   ├── static
│   │   └── css
│   │       └── user_group.css
│   ├── templates
│   │   └── user_group
│   │       ├── ug_delete.html
│   │       ├── ug_detail.html
│   │       ├── ug_list.html
│   │       ├── ug_new.html
│   │       └── ug_update.html
│   ├── tests.py
│   ├── urls.py
│   └── views.py
└── user_profile
    ├── __init__.py
    ├── admin.py
    ├── ajax.py
    ├── forms.py
    ├── migrations
    │   ├── 0001_initial.py
    │   └── __init__.py
    ├── models.py
    ├── static
    │   └── user_profile
    │       └── css
    │           └── user_profile.css
    ├── templates
    │   └── user_profile
    │       ├── user_delete.html
    │       ├── user_detail.html
    │       ├── user_myprofile.html
    │       ├── user_new.html
    │       ├── user_update.html
    │       └── users_list.html
    ├── tests.py
    ├── urls.py
    └── views.py
```