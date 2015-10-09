"""Module related to ua-da sync tasks
"""


from datetime import datetime
import json
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
					scheme + str(ip) + ':' + str(port) + '/local_sync'
					)
		warning('url: {0}'.format(urls))
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
	try:
		os.chdir(SYNC_BASE_DIR)
		files = {'file': ('da_config.tar.gz', open('da_config.tar.gz', 'rb'))}
		r = requests.post(kw.get('url'), files=files)
		res = r.text
	except IOError as exc:
		error('Problem in reading tar file: {0}'.format(exc))
	except requests.exceptions.RequestException as exc:
		error('Problem with the request: {0}'.format(exc))
	else:
		res = json.loads(res)
		warning('API response: {0}'.format(res))
		#if res.get('success') == 1:
		#	retval = True
	
	update_sync_status(retval)

	return retval

