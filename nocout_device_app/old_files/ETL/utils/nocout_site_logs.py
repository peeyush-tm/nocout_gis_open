'''
nocout_site_logs.py
===================

The script to create a logger object which would be used to
log all ETL related activities
'''

import os
import logging
from nocout_site_name import *


def get_site_logger(file_name):
	'''
	Function to create a logging object
	'''
	logger = logging.getLogger('nocout_site_log')
	os.system('mkdir -p /tmp/nocout_da')
	#os.system('chmod 777 /tmp/nocout_da')
	os.system('mkdir -p /tmp/nocout_da/%s' % nocout_site_name)
	fd = os.open('/tmp/nocout_da/%s/%s' % (nocout_site_name, file_name), os.O_RDWR | os.O_CREAT)
	if not len(logger.handlers):
		logger.setLevel(logging.DEBUG)
		handler=logging.FileHandler('/tmp/nocout_da/%s/%s' % (nocout_site_name, file_name))
		formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
		handler.setFormatter(formatter)
		logger.addHandler(handler)
	os.close(fd)

	return logger





