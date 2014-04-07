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
    1. If the installation is with mysql : sudo aptitude install mysqlclient-dev
    2. If the installation is with mariadb : sudo aptitude install mariadbclient-dev
5. Install python-dev - sudo aptitude install python-dev 
6. Install phpmyadmin
7. Create a database named : nocout_dev

**Setup Enviornment**

1. Create folder in /home/<USER>/Document - NOCOUT
2. Change dir - $:~ cd /home/<USER>/Documents/NOCOUT
3. Clone "nocout_gis" repository to this folder (/home/<USER>/Documents/NOCOUT) - $:~ git clone <REPOSITORY-ADDRESS>
4. Create virtualenv - $:~ virtualenv nout
5. Activate virtualenv - (nout):~ source nout/bin/activate
6. Install the requirements for Django app - (nout):~pip install -r requirements.txt
7. 
