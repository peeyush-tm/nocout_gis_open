without supervisor:
	cd /opt/nocout/nocout_gis/ && source /opt/nocout/nout/bin/activate && git pull origin dev_master && cd nocout && python manage.py collectstatic -c --noinput && pkill -HUP uwsgi && cd /opt/nocout/nocout_gis/ && deactivate

with supervisor:
	cd /opt/nocout/nocout_gis/ && source /opt/nocout/nout/bin/activate && git pull origin dev_master && cd nocout && python manage.py collectstatic -c --noinput && sudo supervisorctl restart nocout-uwsgi && cd /opt/nocout/nocout_gis/ && deactivate
