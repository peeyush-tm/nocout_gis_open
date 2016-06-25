"""Module related to ua-da sync tasks
"""


from datetime import datetime
import os
import requests
import tarfile

from celery import chord, group, task
from celery.utils.log import get_task_logger

from django.conf import settings
from device.models import DeviceSyncHistory

import generate_deviceapp_config

logger = get_task_logger(__name__)
info, warning, error = (
		logger.info, logger.warning, logger.error
		)

SYNC_BASE_DIR = settings.BASE_DIR + '/device/sync/'


@task(name='sync-main')
def sync_main(**kw):

	machines = kw.get('machines')

	try:
		generate_deviceapp_config.main()
	except Exception as exc:
		error('Exc in generate config: {0}'.format(exc))
	else:
		try:
			os.chdir(SYNC_BASE_DIR)
			# generate tar file from config files
			out = tarfile.open('da_config.tar.gz', mode='w:gz')
			for entry in os.listdir('.'):
				if entry.endswith('.mk'):
					out.add(entry)
		except Exception as exc:
			error('Exc in tarfile generation: {0}'.format(exc))
		else:
			out.close()
			# call the sync api for all the machines, in parallel
			call_sync_apis.s(machines=machines).apply_async()


@task(name='call-sync-api')
def call_sync_apis(**kw):
	""" Calls sync apis using celery group"""

	scheme = 'http://'
	urls = []
	machines = kw.get('machines')
	if machines:
		for ip, port in machines.iteritems():
			urls.append(
					scheme + str(ip) + ':' + str(port)
					)
		urls = [
				'http://10.133.19.165:5019'
			]
		warning('urls: {0}'.format(urls))
		header = group([get_request.s(url=url) for url in urls]).apply_async()
		#callback = api_callback.s(len(urls))
		#chord(header)(callback)


@task(name='sync-api-callback', time_limit=60*5)
def api_callback(results, task_count):
	""" Task to be called after all the get request return"""

	all_ok = True

	print 'Api results: %s' % results

	# if we didn't receive results for all the tasks
	if len(results) != task_count:
		# update the sync status with non-OK status
		all_ok = False
	else:
		# see if all results are OK
		for r in results:
			if int(r['success']) == 0:
				all_ok = False

	update_sync_status.s(all_ok).apply_async()


@task(name='update-sync-status')
def update_sync_status(successful):

	message = 'Sync '
	status = 1 if successful else 2
	message = message + "successful" if successful else message + 'unsuccessful'
	now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

	try:
		dsho = DeviceSyncHistory.objects.latest('id')
		dsho.status = status
		dsho.message = message
		dsho.completed_on = now
		dsho.save()
	except Exception as exc:
		error('Error in saving sync obj: 0{}'.format(exc))


@task(name='sync-get-request')
def get_request(**kw):
	""" Sends the get request using requests"""

	retval = False

	url = kw.get('url')
	sync_api = url + '/local_sync'
	restart_api = url + '/restart'

	warning('sync_api: {0}, restart_api: {1}'.format(sync_api, restart_api))

	try:
		os.chdir(SYNC_BASE_DIR)
		files = {'file': ('da_config.tar.gz', open('da_config.tar.gz', 'rb'))}
		r = requests.post(sync_api, files=files)
		res = r.text
		status_code = r.status_code
	except IOError as exc:
		error('Problem in reading tar file: {0}'.format(exc))
	except Exception as exc:
		error('Error in sending request: {0}'.format(exc))
	else:
		try:
			jsn_res = r.json()
			warning('Sync Response: {0}'.format(jsn_res))
			if status_code == 200 and jsn_res.get('success') == 1:
				retval = True
				# restart monitoring core
				r = requests.post(restart_api)
				warning('Restart Response: {0}'.format(r.text))
		except Exception as exc:
			error('Error in response: {0}'.format(exc))
	
	update_sync_status(retval)

	return retval

