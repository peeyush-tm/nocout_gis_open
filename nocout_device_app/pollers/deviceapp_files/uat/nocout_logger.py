from wato import defaults
import logging
import os


def nocout_log():
	"""
	Handles logging functionality for device app

	Returns:
	        Returns the logger object, which logs the
		activities to a file
	"""
	logger=logging.getLogger('nocout_da')
	os.system('mkdir -p /tmp/nocout_da')
	os.system('chmod 777 /tmp/nocout_da')
	os.system('mkdir -p /tmp/nocout_da/%s' % defaults.omd_site)
	fd = os.open('/tmp/nocout_da/%s/nocout_live.log' % defaults.omd_site, os.O_RDWR | os.O_CREAT)
	if not len(logger.handlers):
		logger.setLevel(logging.DEBUG)
		handler=logging.FileHandler('/tmp/nocout_da/%s/nocout_live.log' % defaults.omd_site)
		formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
		handler.setFormatter(formatter)
		handler.setFormatter(formatter)
		logger.addHandler(handler)
	os.close(fd)

	return logger
