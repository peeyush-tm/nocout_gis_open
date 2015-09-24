"""Module related to ua-da sync tasks
"""


from datetime import datetime
import os
import requests
import tarfile

from celery import chord, task
from celery.utils.log import get_task_logger

from django.conf.settings import BASE_DIR
from device.models import DeviceSyncHistory
import generate_deviceapp_config

logger = get_task_logger(__name__)
info, warning, error = (
		logger.info, logger.warning, logger.error
		)


@task(name='sync-main')
def sync_main(**kw):

	machines = kw.get('machines')
	sync_base_dir = BASE_DIR + '/device/sync/'

	try:
		generate_deviceapp_config.main()
	except Exception as exc:
		error('Exc in generate config: {0}'.format(exc))
	else:
		try:
			os.chdir(sync_base_dir)
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
		for m in machines.iteritems():
			urls.append(
					scheme + m.get('machine_ip') + ':' + \
							m.get('siteinstance__web_service_port') + '/local_sync'
					)

		header = [get_request.s(url=url) for url in urls]
		callback = api_callback.s(len(urls))
		chord(header)(callback)


@task(name='sync-api-callback')
def api_callback(results, task_count):
	""" Task to be called after all the get request return"""

	all_ok = True

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
	now = datetime.now().strftime('%Y-%m-%d-%H-%M-%S')

	try:
		dsho = DeviceSyncHistory.objects.latest('id')
		dsho.status = status
		dsho.message = message
		dsho.completed_on = now
		dsho.save()
	except Exception as exc:
		error('Error in saving sync obj: 0{}'.format(exc))


@task(name='sync-get-request', time_limit=60*30)
def get_request(**kw):
	""" Sends the get request using requests"""

	r = requests.get(kw.get('url'))
	return r.json()

