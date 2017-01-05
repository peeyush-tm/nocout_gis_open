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

**Setup RHEL/CENTOS Server**

1. Go to /home/tmadmin/DEPLOYED/Packages/machine-packages/0-0-0-pm
```
sudo yum install 0-0-0-pm/cloog-ppl-0.15.7-1.2.el6.x86_64.rpm 0-0-0-pm/cloog-ppl-devel-0.15.7-1.2.el6.x86_64.rpm 0-0-0-pm/cpp-4.4.7-4.el6.x86_64.rpm 0-0-0-pm/expat-devel-2.0.1-11.el6_2.x86_64.rpm 0-0-0-pm/gmp-devel-4.3.1-7.el6_2.2.x86_64.rpm 0-0-0-pm/gnutls-2.8.5-10.el6_4.2.x86_64.rpm 0-0-0-pm/gnutls-2.8.5-14.el6_5.x86_64.rpm 0-0-0-pm/gnutls-devel-2.8.5-14.el6_5.x86_64.rpm 0-0-0-pm/gnutls-utils-2.8.5-14.el6_5.x86_64.rpm 0-0-0-pm/libgcrypt-devel-1.4.5-11.el6_4.x86_64.rpm 0-0-0-pm/libgpg-error-devel-1.7-4.el6.x86_64.rpm 0-0-0-pm/mpfr-2.4.1-6.el6.x86_64.rpm 0-0-0-pm/neon-0.29.3-3.el6_4.x86_64.rpm 0-0-0-pm/neon-devel-0.29.3-3.el6_4.x86_64.rpm 0-0-0-pm/pakchois-0.4-3.2.el6.x86_64.rpm 0-0-0-pm/pakchois-devel-0.4-3.2.el6.x86_64.rpm 0-0-0-pm/ppl-0.10.2-11.el6.x86_64.rpm 0-0-0-pm/ppl-devel-0.10.2-11.el6.x86_64.rpm 0-0-0-pm/zlib-devel-1.2.3-29.el6.x86_64.rpm
```
```shell
sudo yum install install 0-0-pre-machine/apr-1.3.9-5.el6_2.x86_64.rpm 0-0-pre-machine/apr-devel-1.3.9-5.el6_2.x86_64.rpm 0-0-pre-machine/apr-util-1.3.9-3.el6_0.1.x86_64.rpm 0-0-pre-machine/apr-util-devel-1.3.9-3.el6_0.1.x86_64.rpm 0-0-pre-machine/autoconf-2.63-5.1.el6.noarch.rpm 0-0-pre-machine/automake-1.11.1-4.el6.noarch.rpm 0-0-pre-machine/bison-2.4.1-5.el6.x86_64.rpm 0-0-pre-machine/byacc-1.9.20070509-7.el6.x86_64.rpm 0-0-pre-machine/cscope-15.6-6.el6.x86_64.rpm 0-0-pre-machine/ctags-5.8-2.el6.x86_64.rpm 0-0-pre-machine/cvs-1.11.23-16.el6.x86_64.rpm 0-0-pre-machine/cyrus-sasl-devel-2.1.23-13.el6_3.1.x86_64.rpm 0-0-pre-machine/db4-cxx-4.7.25-18.el6_4.x86_64.rpm 0-0-pre-machine/db4-devel-4.7.25-18.el6_4.x86_64.rpm 0-0-pre-machine/diffstat-1.51-2.el6.x86_64.rpm 0-0-pre-machine/doxygen-1.6.1-6.el6.x86_64.rpm 0-0-pre-machine/expat-devel-2.0.1-11.el6_2.x86_64.rpm 0-0-pre-machine/flex-2.5.35-8.el6.x86_64.rpm 0-0-pre-machine/gcc-4.4.7-4.el6.x86_64.rpm 0-0-pre-machine/gcc-c++-4.4.7-4.el6.x86_64.rpm 0-0-pre-machine/gcc-gfortran-4.4.7-4.el6.x86_64.rpm 0-0-pre-machine/gdb-7.2-64.el6_5.2.x86_64.rpm 0-0-pre-machine/gettext-0.17-16.el6.x86_64.rpm 0-0-pre-machine/gettext-devel-0.17-16.el6.x86_64.rpm 0-0-pre-machine/gettext-libs-0.17-16.el6.x86_64.rpm 0-0-pre-machine/git-1.7.1-3.el6_4.1.x86_64.rpm 0-0-pre-machine/gmp-devel-4.3.1-7.el6_2.2.x86_64.rpm 0-0-pre-machine/indent-2.2.10-7.el6.x86_64.rpm 0-0-pre-machine/intltool-0.41.0-1.1.el6.noarch.rpm 0-0-pre-machine/kernel-devel-2.6.32-431.23.3.el6.x86_64.rpm 0-0-pre-machine/libart_lgpl-2.3.20-5.1.el6.x86_64.rpm 0-0-pre-machine/libart_lgpl-devel-2.3.20-5.1.el6.x86_64.rpm 0-0-pre-machine/libgcj-4.4.7-4.el6.x86_64.rpm 0-0-pre-machine/libgfortran-4.4.7-4.el6.x86_64.rpm 0-0-pre-machine/libstdc++-devel-4.4.7-4.el6.x86_64.rpm 0-0-pre-machine/libtool-2.2.6-15.5.el6.x86_64.rpm 0-0-pre-machine/mpfr-2.4.1-6.el6.x86_64.rpm 0-0-pre-machine/mpfr-devel-2.4.1-6.el6.x86_64.rpm 0-0-pre-machine/openldap-2.4.23-32.el6_4.1.x86_64.rpm 0-0-pre-machine/openldap-2.4.23-34.el6_5.1.x86_64.rpm 0-0-pre-machine/openldap-devel-2.4.23-34.el6_5.1.x86_64.rpm 0-0-pre-machine/patchutils-0.3.1-3.1.el6.x86_64.rpm 0-0-pre-machine/perl-Compress-Raw-Zlib-2.021-136.el6.x86_64.rpm 0-0-pre-machine/perl-Compress-Zlib-2.021-136.el6.x86_64.rpm 0-0-pre-machine/perl-Error-0.17015-4.el6.noarch.rpm 0-0-pre-machine/perl-Git-1.7.1-3.el6_4.1.noarch.rpm 0-0-pre-machine/perl-HTML-Parser-3.64-2.el6.x86_64.rpm 0-0-pre-machine/perl-HTML-Tagset-3.20-4.el6.noarch.rpm 0-0-pre-machine/perl-IO-Compress-Base-2.021-136.el6.x86_64.rpm 0-0-pre-machine/perl-IO-Compress-Zlib-2.021-136.el6.x86_64.rpm 0-0-pre-machine/perl-libwww-perl-5.833-2.el6.noarch.rpm 0-0-pre-machine/perl-URI-1.40-2.el6.noarch.rpm 0-0-pre-machine/perl-XML-Parser-2.36-7.el6.x86_64.rpm 0-0-pre-machine/rcs-5.7-37.el6.x86_64.rpm 0-0-pre-machine/redhat-rpm-config-9.0.3-42.el6.centos.noarch.rpm 0-0-pre-machine/rpm-build-4.8.0-37.el6.x86_64.rpm 0-0-pre-machine/subversion-1.6.11-10.el6_5.x86_64.rpm 0-0-pre-machine/swig-1.3.40-6.el6.x86_64.rpm 0-0-pre-machine/systemtap-2.3-4.el6_5.x86_64.rpm 0-0-pre-machine/systemtap-client-2.3-4.el6_5.x86_64.rpm 0-0-pre-machine/systemtap-devel-2.3-4.el6_5.x86_64.rpm 0-0-pre-machine/systemtap-runtime-2.3-4.el6_5.x86_64.rpm
```
```
install 0-1-pre-machine/bzip2-devel-1.0.5-7.el6_0.x86_64.rpm 0-1-pre-machine/db4-cxx-4.7.25-18.el6_4.x86_64.rpm 0-1-pre-machine/db4-devel-4.7.25-18.el6_4.x86_64.rpm 0-1-pre-machine/e2fsprogs-1.41.12-18.el6_5.1.x86_64.rpm 0-1-pre-machine/e2fsprogs-1.41.12-18.el6.x86_64.rpm 0-1-pre-machine/e2fsprogs-libs-1.41.12-18.el6_5.1.x86_64.rpm 0-1-pre-machine/e2fsprogs-libs-1.41.12-18.el6.x86_64.rpm 0-1-pre-machine/glibc-2.12-1.132.el6_5.2.x86_64.rpm 0-1-pre-machine/glibc-2.12-1.132.el6.x86_64.rpm 0-1-pre-machine/glibc-common-2.12-1.132.el6_5.2.x86_64.rpm 0-1-pre-machine/glibc-common-2.12-1.132.el6.x86_64.rpm 0-1-pre-machine/glibc-devel-2.12-1.132.el6_5.2.x86_64.rpm 0-1-pre-machine/glibc-devel-2.12-1.132.el6.x86_64.rpm 0-1-pre-machine/glibc-headers-2.12-1.132.el6_5.2.x86_64.rpm 0-1-pre-machine/glibc-headers-2.12-1.132.el6.x86_64.rpm 0-1-pre-machine/keyutils-libs-devel-1.4-4.el6.x86_64.rpm 0-1-pre-machine/krb5-devel-1.10.3-15.el6_5.1.x86_64.rpm 0-1-pre-machine/krb5-libs-1.10.3-15.el6_5.1.x86_64.rpm 0-1-pre-machine/krb5-workstation-1.10.3-15.el6_5.1.x86_64.rpm 0-1-pre-machine/libcom_err-1.41.12-18.el6_5.1.x86_64.rpm 0-1-pre-machine/libcom_err-1.41.12-18.el6.x86_64.rpm 0-1-pre-machine/libcom_err-devel-1.41.12-18.el6_5.1.x86_64.rpm 0-1-pre-machine/libpcap-devel-1.4.0-1.20130826git2dbcaa1.el6.x86_64.rpm 0-1-pre-machine/libselinux-devel-2.0.94-5.3.el6_4.1.x86_64.rpm 0-1-pre-machine/libselinux-python-2.0.94-5.3.el6_4.1.x86_64.rpm 0-1-pre-machine/libsepol-devel-2.0.41-4.el6.x86_64.rpm 0-1-pre-machine/libss-1.41.12-18.el6_5.1.x86_64.rpm 0-1-pre-machine/libss-1.41.12-18.el6.x86_64.rpm 0-1-pre-machine/ncurses-devel-5.7-3.20090208.el6.x86_64.rpm 0-1-pre-machine/nss-softokn-freebl-3.14.3-10.el6_5.x86_64.rpm 0-1-pre-machine/nss-softokn-freebl-3.14.3-9.el6.x86_64.rpm 0-1-pre-machine/openssl-1.0.1e-16.el6_5.14.x86_64.rpm 0-1-pre-machine/openssl-devel-1.0.1e-16.el6_5.14.x86_64.rpm 0-1-pre-machine/readline-devel-6.0-4.el6.x86_64.rpm 0-1-pre-machine/sqlite-devel-3.6.20-1.el6.x86_64.rpm
0-1-pre-machine/xz-devel-4.999.9-0.3.beta.20091007git.el6.x86_64.rpm 0-1-pre-machine/zlib-devel-1.2.3-29.el6.x86_64.rpm
```
```
sudo yum install  0-2-pre-machine/audit-2.2-4.el6_5.x86_64.rpm 0-2-pre-machine/audit-libs-2.2-4.el6_5.x86_64.rpm 0-2-pre-machine/audit-libs-python-2.2-4.el6_5.x86_64.rpm 0-2-pre-machine/libcgroup-0.40.rc1-5.el6_5.1.x86_64.rpm 0-2-pre-machine/libsemanage-python-2.0.43-4.2.el6.x86_64.rpm 0-2-pre-machine/policycoreutils-python-2.0.83-19.39.el6.x86_64.rpm 0-2-pre-machine/setools-libs-3.3.7-4.el6.x86_64.rpm 0-2-pre-machine/setools-libs-python-3.3.7-4.el6.x86_64.rpm
```
6. `sudo yum  install geos-3.3.2-1.el6.x86_64.rpm geos-devel-3.3.2-1.el6.x86_64.rpm geos-python-3.3.2-1.el6.x86_64.rpm`
7. Go to /home/tmadmin/DEPLOYED/Packages/setup-packages/1-python-post/device_app_pckgs
8. Go to /home/tmadmin/DEPLOYED/Packages/setup-packages/2-omd-pre/
```
sudo yum install apr-devel-1.3.9-5.el6_2.x86_64.rpm apr-util-devel-1.3.9-3.el6_0.1.x86_64.rpm apr-util-ldap-1.3.9-3.el6_0.1.x86_64.rpm bind-libs-9.8.2-0.23.rc1.el6_5.1.x86_64.rpm bind-utils-9.8.2-0.23.rc1.el6_5.1.x86_64.rpm boost-1.41.0-18.el6.x86_64.rpm boost-date-time-1.41.0-18.el6.x86_64.rpm boost-devel-1.41.0-18.el6.x86_64.rpm boost-filesystem-1.41.0-18.el6.x86_64.rpm boost-graph-1.41.0-18.el6.x86_64.rpm boost-iostreams-1.41.0-18.el6.x86_64.rpm boost-math-1.41.0-18.el6.x86_64.rpm boost-program-options-1.41.0-18.el6.x86_64.rpm boost-python-1.41.0-18.el6.x86_64.rpm boost-regex-1.41.0-18.el6.x86_64.rpm boost-serialization-1.41.0-18.el6.x86_64.rpm boost-signals-1.41.0-18.el6.x86_64.rpm boost-system-1.41.0-18.el6.x86_64.rpm boost-test-1.41.0-18.el6.x86_64.rpm boost-thread-1.41.0-18.el6.x86_64.rpm boost-wave-1.41.0-18.el6.x86_64.rpm cairo-devel-1.8.8-3.1.el6.x86_64.rpm compat-readline5-5.2-17.1.el6.x86_64.rpm curl-7.19.7-37.el6_5.3.x86_64.rpm cyrus-sasl-devel-2.1.23-13.el6_3.1.x86_64.rpm db4-cxx-4.7.25-18.el6_4.x86_64.rpm db4-devel-4.7.25-18.el6_4.x86_64.rpm dialog-1.1-9.20080819.1.el6.x86_64.rpm dialog-devel-1.1-9.20080819.1.el6.x86_64.rpm e2fsprogs-1.41.12-18.el6_5.1.x86_64.rpm e2fsprogs-libs-1.41.12-18.el6_5.1.x86_64.rpm expat-devel-2.0.1-11.el6_2.x86_64.rpm fontconfig-devel-2.8.0-3.el6.x86_64.rpm fping-2.4b2-10.el6.x86_64.rpm freetype-devel-2.3.11-14.el6_3.1.x86_64.rpm gd-2.0.35-11.el6.x86_64.rpm gdbm-devel-1.8.0-36.el6.x86_64.rpm gd-devel-2.0.35-11.el6.x86_64.rpm geos-3.3.2-1.el6.x86_64.rpm geos-devel-3.3.2-1.el6.x86_64.rpm geos-python-3.3.2-1.el6.x86_64.rpm glib2-2.26.1-7.el6_5.x86_64.rpm glib2-devel-2.26.1-7.el6_5.x86_64.rpm httpd-2.2.15-31.el6.centos.x86_64.rpm httpd-devel-2.2.15-31.el6.centos.x86_64.rpm httpd-tools-2.2.15-31.el6.centos.x86_64.rpm keyutils-libs-devel-1.4-4.el6.x86_64.rpm krb5-devel-1.10.3-15.el6_5.1.x86_64.rpm krb5-libs-1.10.3-15.el6_5.1.x86_64.rpm libblkid-2.17.2-12.14.el6_5.x86_64.rpm libcom_err-1.41.12-18.el6_5.1.x86_64.rpm libcom_err-devel-1.41.12-18.el6_5.1.x86_64.rpm libcurl-7.19.7-37.el6_5.3.x86_64.rpm libcurl-devel-7.19.7-37.el6_5.3.x86_64.rpm libevent-1.4.13-4.el6.x86_64.rpm libevent-devel-1.4.13-4.el6.x86_64.rpm libevent-doc-1.4.13-4.el6.noarch.rpm libevent-headers-1.4.13-4.el6.noarch.rpm libicu-4.2.1-9.1.el6_2.x86_64.rpm libidn-devel-1.18-2.el6.x86_64.rpm libjpeg-turbo-1.2.1-3.el6_5.x86_64.rpm libjpeg-turbo-devel-1.2.1-3.el6_5.x86_64.rpm libmcrypt-2.5.8-9.el6.x86_64.rpm libmcrypt-devel-2.5.8-9.el6.x86_64.rpm libpng-devel-1.2.49-1.el6_2.x86_64.rpm libselinux-devel-2.0.94-5.3.el6_4.1.x86_64.rpm libsepol-devel-2.0.41-4.el6.x86_64.rpm libsmbclient-3.6.9-169.el6_5.x86_64.rpm libss-1.41.12-18.el6_5.1.x86_64.rpm libtool-ltdl-2.2.6-15.5.el6.x86_64.rpm libtool-ltdl-devel-2.2.6-15.5.el6.x86_64.rpm libuuid-2.17.2-12.14.el6_5.x86_64.rpm libuuid-devel-2.17.2-12.14.el6_5.x86_64.rpm libX11-devel-1.5.0-4.el6.x86_64.rpm libXau-devel-1.0.6-4.el6.x86_64.rpm libXaw-1.0.11-2.el6.x86_64.rpm libxcb-devel-1.8.1-1.el6.x86_64.rpm libXdmcp-1.1.1-3.el6.x86_64.rpm libXdmcp-devel-1.1.1-3.el6.x86_64.rpm libXext-devel-1.3.1-2.el6.x86_64.rpm libXft-devel-2.3.1-2.el6.x86_64.rpm libxkbfile-1.0.6-1.1.el6.x86_64.rpm libxml2-2.7.6-14.el6_5.2.x86_64.rpm libxml2-devel-2.7.6-14.el6_5.2.x86_64.rpm libxml2-python-2.7.6-14.el6_5.2.x86_64.rpm libXpm-3.5.10-2.el6.x86_64.rpm libXpm-devel-3.5.10-2.el6.x86_64.rpm libXrender-devel-0.9.7-2.el6.x86_64.rpm mod_fcgid-2.3.9-1.el6.x86_64.rpm ncurses-devel-5.7-3.20090208.el6.x86_64.rpm net-snmp-5.5-49.el6_5.1.x86_64.rpm net-snmp-libs-5.5-49.el6_5.1.x86_64.rpm net-snmp-utils-5.5-49.el6_5.1.x86_64.rpm openldap-2.4.23-34.el6_5.1.x86_64.rpm openldap-devel-2.4.23-34.el6_5.1.x86_64.rpm openssl-1.0.1e-16.el6_5.14.x86_64.rpm openssl-devel-1.0.1e-16.el6_5.14.x86_64.rpm pango-devel-1.28.1-7.el6_3.x86_64.rpm pcre-devel-7.8-6.el6.x86_64.rpm perl-Crypt-DES-2.05-9.el6.x86_64.rpm perl-devel-5.10.1-136.el6.x86_64.rpm perl-Digest-HMAC-1.01-22.el6.noarch.rpm perl-Digest-SHA1-2.12-2.el6.x86_64.rpm perl-Digest-SHA-5.47-136.el6.x86_64.rpm perl-ExtUtils-Embed-1.28-136.el6.x86_64.rpm perl-ExtUtils-MakeMaker-6.55-136.el6.x86_64.rpm perl-ExtUtils-ParseXS-2.2003.0-136.el6.x86_64.rpm perl-Net-SNMP-5.2.0-4.el6.noarch.rpm perl-Test-Harness-3.17-136.el6.x86_64.rpm perl-Time-HiRes-1.9721-136.el6.x86_64.rpm php-5.3.3-27.el6_5.1.x86_64.rpm php-cli-5.3.3-27.el6_5.1.x86_64.rpm php-common-5.3.3-27.el6_5.1.x86_64.rpm pixman-0.26.2-5.1.el6_5.x86_64.rpm pixman-devel-0.26.2-5.1.el6_5.x86_64.rpm python-2.6.6-52.el6.x86_64.rpm python-devel-2.6.6-52.el6.x86_64.rpm python-libs-2.6.6-52.el6.x86_64.rpm readline-devel-6.0-4.el6.x86_64.rpm samba-client-3.6.9-169.el6_5.x86_64.rpm samba-common-3.6.9-169.el6_5.x86_64.rpm samba-winbind-3.6.9-169.el6_5.x86_64.rpm samba-winbind-clients-3.6.9-169.el6_5.x86_64.rpm util-linux-ng-2.17.2-12.14.el6_5.x86_64.rpm xinetd-2.3.14-39.el6_4.x86_64.rpm xkeyboard-config-2.6-6.el6.noarch.rpm xorg-x11-proto-devel-7.6-25.el6.noarch.rpm xorg-x11-server-common-1.13.0-23.1.el6.centos.x86_64.rpm xorg-x11-server-Xvfb-1.13.0-23.1.el6.centos.x86_64.rpm xorg-x11-xkb-extras-7.7-4.el6.x86_64.rpm xorg-x11-xkb-utils-7.7-4.el6.x86_64.rpm zlib-devel-1.2.3-29.el6.x86_64.rpm
```
10. Go to /home/tmadmin/DEPLOYED/Packages/setup-packages/
11. Go to /home/tmadmin/DEPLOYED/Packages/setup-packages/1-python-post
12. `easy_install device_app_pckgs/six-1.4.1.tar.gz`
13. `easy_install device_app_pckgs/configobj-5.0.5.tar.gz`
14. `easy_install device_app_pckgs/demjson-2.2.2.tar.gz`
15. `easy_install device_app_pckgs/mysql-connector-python-1.2.2.zip`
16. `easy_install device_app_pckgs/pymongo-2.7.2.tar.gz `
17. Go to /home/tmadmin/DEPLOYED/Packages/setup-packages/4-graphviz-pre
```
sudo install 4-graphviz-pre/ann-1.1.1-4.el6.x86_64.rpm 4-graphviz-pre/ann-devel-1.1.1-4.el6.x86_64.rpm 4-graphviz-pre/ann-libs-1.1.1-4.el6.x86_64.rpm 4-graphviz-pre/gts-0.7.6-19.20111025.el6.x86_64.rpm 4-graphviz-pre/gts-devel-0.7.6-19.20111025.el6.x86_64.rpm 4-graphviz-pre/netpbm-10.47.05-11.el6.x86_64.rpm
```
19. Go to /home/tmadmin/DEPLOYED/Packages/setup-packages/4-graphviz
```
sudo yum install install graphviz-2.38.0-1.el6.x86_64.rpm graphviz-libs-2.38.0-1.el6.x86_64.rpm graphviz-plugins-core-2.38.0-1.el6.x86_64.rpm graphviz-gd-2.38.0-1.el6.x86_64.rpm graphviz-plugins-gd-2.38.0-1.el6.x86_64.rpm graphviz-lang-php-2.38.0-1.el6.x86_64.rpm graphviz-lang-python-2.38.0-1.el6.x86_64.rpm graphviz-devel-2.38.0-1.el6.x86_64.rpm graphviz-graphs-2.38.0-1.el6.noarch.rpm
```
21. go to /home/tmadmin/DEPLOYED/Packages/setup-packages/3-omd/
22. Copy omd-1.10-src-base-omd /omd/
23. tar -xzvf omd-1.10-src-base-omd.tgz 
24. cd omd-6.5
25. Change the Makefile for distros/Makefile.RHEL6.5 
26. Change the Make file for Makefile (Install OMD (remove the packages PERL DBD MySQL install it later)
27. Change the Makefile for Makefile.omd
28. Change the Makefile for packages/perl-modules/Perl-DBD-mysql (Install OMD (remove the packages PERL DBD MySQL install it later)
29. Allow /etc/cron.allow (with tmadmin user and with site user)
30. Optional 26. Install Python (done)
31. Optional 27. Install PIP 
32. Optional 28. Install Virtualenv for python2.7
33. Apps Configuration 29. Configure Check - Mk : htdocs/defaults.py file, change the name for %site (site will now be 4)
34. Apps Configuration 30. Configure Check - Mk : search and comment : apache.log_error
35. Optional 31. export path to : /apps/python27/bin 
36. export path to /apps/mysql/bin
37. export path to : /apps/omd/bin 
38. set $MYSQL_HOME
39. change the /etc/ld.conf.d/mysql-x86_64 : path to libraries
40. export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:/apps/mysql/lib
41. run : ldconfig -v	
42. mysql : GRANT ALL PRIVILAGES ON *.* TO 'root'@'%' WITH GRANT OPTION;
43. mysqladmin : mysqladmin -u root password 'root'


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

**M7 UA New Packages: Monitoring Tool for Celery : flower**

1. pip install backports.ssl_match_hostname-3.4.0.2.tar.gz certifi-2015.04.28.tar.gz tornado-4.1.tar.gz pytz-2015.2.tar.bz2 futures-3.0.1.tar.gz backports.ssl_match_hostname-3.4.0.2.tar.gz Babel-1.3.tar.gz certifi-2015.04.28.tar.gz flower-0.8.2.tar.gz
2. Packages available in `requirements/requirements_user_app/Celery/2015-05-MAY-06`

**Update SNMPTT trap handler to snmptthandler-embedded**

1. Install net-snmp-perl package
    ```
    sudo yum install net-snmp-perl
    ```
2. Create a file snmptthandler-embedded

    ```
    vim usr/sbin/snmptthandler-embedded
    ```
    And paste the content of the snmptthandler-embedded file available at location `nocout_device_app/trap_handler` in it.
    
3. Update snmptrapd.conf

    ```
    sudo vim /etc/snmp/snmptrapd.conf
    ```
    
    Replace :
    
    ```
    traphandle default /usr/sbin/snmptthandler
    ```
    
    With :
    
    ```
    perl do "/usr/sbin/snmptthandler-embedded";
    ```
    
4. Restart snmptrapd service

    ```
    sudo service snmptrapd restart
    ```
    
5. Restart snmptt service

    ```
    sudo service snmptt restart
    ```
    

