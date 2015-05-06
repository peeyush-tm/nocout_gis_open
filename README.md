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


**SETTINGS : Cache Setup : 16th March**

1. Use Redis as cache [ replaced memcached ]
2. Install : django-redis
3. Install : hiredis
4. Packages available in : `requirements/requirements_user_app/Cache/16\ March\ 2015/`

**New Package : Bootstrap Breadcrumbs Django : 23rd March**

1. For displaying breadcrumbs in the application
2. Install : django-bootstrap-breadcrumbs
3. packages available in `requirements/requirements_user_app/Base/Breadcrumbs-March-23-15/`

TODO:

1. Dynamic Breadcrumbs

**New Package : SIMPLEJSON : 23rd March**

1. For reports via celery
2. Install : simplejson
3. packages available in `requirements/requirements_user_app/Celery/SIMPLEJSON-March-23-15/`

**New Package : django-settings-export : 25th March**

1. For accessing Settings Variables in TEMPLATES
2. Install : django-settings-export
3. Link : https://github.com/jakubroztocil/django-settings-export
4. Package Available in `requirements/requirements_user_app/Base/TempateSettings-March-25-15`

**M7 DA New Package: python-memcached-1.54 29th April**

1. For Deploying python-memcached
2. Install :python-memcached-1.54
3. Package Available in requirements/requirements_device_app/

**M7 DA New Package: memcached-1.4.4-3 29th April**

1. For Deploying python-memcached
2. Install : memcached-1.4.4-3
3. Package Available in requirements/requirements_user_app/Cache/24November/0-memcached/

** M7 UA New Packages: Monitoring Tool for Celery : flower

1. pip install backports.ssl_match_hostname-3.4.0.2.tar.gz certifi-2015.04.28.tar.gz tornado-4.1.tar.gz pytz-2015.2.tar.bz2 futures-3.0.1.tar.gz backports.ssl_match_hostname-3.4.0.2.tar.gz Babel-1.3.tar.gz certifi-2015.04.28.tar.gz flower-0.8.2.tar.gz
2. Packages available in `requirements/requirements_user_app/Celery/2015-05-MAY-06`
