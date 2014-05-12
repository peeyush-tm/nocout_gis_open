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
    1. If the installation is with mysql : sudo aptitude install mysqlclient-dev mysqlclient-dev
    2. If the installation is with mariadb : sudo aptitude install mariadbclient-dev libmariadbclient-dev
5. Install python-dev - sudo aptitude install python-dev 
6. Install phpmyadmin
7. Create a database named : nocout_dev
8. Install graphviz -  sudo aptitude install graphviz
9. Install Python Wrapper to graphwiz - sudo aptitude install python-pygraphviz
10. Install Shared liberaries graphviz & python -  sudo aptitude install libgraphviz-dev

**Setup Enviornment**

1. Create folder in /home/<USER>/Document - NOCOUT
2. Change dir - $:~ cd /home/<USER>/Documents/NOCOUT
3. Clone "nocout_gis" repository to this folder (/home/<USER>/Documents/NOCOUT) - $:~ git clone <REPOSITORY-ADDRESS>
4. Go to the cloned repository folder : cd /home/<USER>/Documents/NOCOUT/nocout_gis
5. Create virtualenv - $:~ virtualenv nout
6. Activate virtualenv - (nout):~ source nout/bin/activate
7. Install the requirements for Django app - (nout):~pip install -r requirements.txt 
