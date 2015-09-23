#!/usr/bin/python


"""This Class is an Arbiter module for having a webservice
throuhg which we can have `sync` and `live polling` functionalities
"""


import os
import select
import tarfile
import time

from shinken.basemodule import BaseModule
from shinken.external_command import ExternalCommand
from shinken.log import logger
from shinken.webui.bottlewebui import (run, route, request, 
		response, abort, check_auth, parse_auth)

from nocout_live import main as live_poll_main

properties = {
	'daemons': ['arbiter', 'receiver'],
	'type': 'ws_nocout',
	'external': True,
	}


# called by the plugin manager to get a broker
def get_instance(plugin):
	# info("[WS_Nocout] get_instance ...")
	instance = WsNocout(plugin)
	return instance

# Main app var. Will be fill with our running module instance
app = None

# Check_MK home dir
check_mk_conf_path = '/omd/dev_slave/slave_2/etc/check_mk/conf.d/wato/'
check_mk_bin = '/omd/dev_slave/slave_2/bin/cmk'


def get_commands(time_stamps, hosts, services, return_codes, outputs):
	"""Composing a command list based on the information received in
	POST request
	"""

	commands = []

	current_time_stamp = int(time.time())

	def _compose_command(t, h, s, r, o):
		"""Simple function to create a command from the inputs"""
		cmd = ""
		if not s or s == "":
			cmd = '[%s] PROCESS_HOST_CHECK_RESULT;%s;%s;%s' % (t if t is not None else current_time_stamp, h, r, o)
		else:
			cmd = '[%s] PROCESS_SERVICE_CHECK_RESULT;%s;%s;%s;%s' % (t if t is not None else current_time_stamp, h, s, r, o)
		logger.debug("[WS_Nocout] CMD: %s" % (cmd))
		commands.append(cmd)

	# Trivial case: empty commmand list
	if (return_codes is None or len(return_codes) == 0):
		return commands

	# Sanity check: if we get N return codes, we must have N hosts.
	# The other values could be None
	if (len(return_codes) != len(hosts)):
		logger.error("[WS_Nocout] number of return codes (%d) does not match number of hosts (%d)" % (len(return_codes), len(hosts)))
		abort(400, "number of return codes does not match number of hosts")

	map(_compose_command, time_stamps, hosts, services, return_codes, outputs)
	logger.debug("[WS_Nocout] received command: %s" % (str(commands)))
	return commands


def get_page():
	commands_list = []

	try:
		# Getting lists of informations for the commands
		time_stamp_list = []
		host_name_list = []
		service_description_list = []
		return_code_list = []
		output_list = []
		time_stamp_list = request.forms.getall(key='time_stamp')
		logger.debug("[WS_Nocout] time_stamp_list: %s" % (time_stamp_list))
		host_name_list = request.forms.getall(key='host_name')
		logger.debug("[WS_Nocout] host_name_list: %s" % (host_name_list))
		service_description_list = request.forms.getall(key='service_description')
		logger.debug("[WS_Nocout] service_description_list: %s" % (service_description_list))
		return_code_list = request.forms.getall(key='return_code')
		logger.debug("[WS_Nocout] return_code_list: %s" % (return_code_list))
		output_list = request.forms.getall(key='output')
		logger.debug("[WS_Nocout] output_list: %s" % (output_list))
		commands_list = get_commands(time_stamp_list, host_name_list, service_description_list, return_code_list, output_list)
	except Exception, e:
		logger.error("[WS_Nocout] failed to get the lists: %s" % str(e))
		commands_list = []

	#check_auth()

	# Adding commands to the main queue()
	logger.debug("[WS_Nocout] commands: %s" % str(sorted(commands_list)))
	for c in sorted(commands_list):
		ext = ExternalCommand(c)
		app.from_q.put(ext)

	# OK here it's ok, it will return a 200 code


def do_restart():
	# Getting lists of informations for the commands
	time_stamp = request.forms.get('time_stamp', int(time.time()))
	command = '[%s] RESTART_PROGRAM\n' % time_stamp

	check_auth()

	# Adding commands to the main queue()
	logger.warning("[WS_Nocout] command: %s" % str(command))
	ext = ExternalCommand(command)
	app.from_q.put(ext)

	# OK here it's ok, it will return a 200 code


def do_reload():
	# Getting lists of informations for the commands
	time_stamp = request.forms.get('time_stamp', int(time.time()))
	command = '[%s] RELOAD_CONFIG\n' % time_stamp

	check_auth()

	# Adding commands to the main queue()
	logger.warning("[WS_Nocout] command: %s" % str(command))
	ext = ExternalCommand(command)
	app.from_q.put(ext)

	# OK here it's ok, it will return a 200 code


def do_recheck():
	# Getting lists of informations for the commands
	time_stamp		  = request.forms.get('time_stamp', int(time.time()))
	host_name		   = request.forms.get('host_name', '')
	service_description = request.forms.get('service_description', '')
	logger.debug("[WS_Nocout] Timestamp '%s' - host: '%s', service: '%s'" % (time_stamp,
																			  host_name,
																			  service_description
																			 )
				)

	if not host_name:
		abort(400, 'Missing parameter host_name')

	if service_description:
		# SCHEDULE_FORCED_SVC_CHECK;<host_name>;<service_description>;<check_time>
		command = '[%s] SCHEDULE_FORCED_SVC_CHECK;%s;%s;%s\n' % (time_stamp,
																 host_name,
																 service_description,
																 time_stamp)
	else:
		# SCHEDULE_FORCED_HOST_CHECK;<host_name>;<check_time>
		command = '[%s] SCHEDULE_FORCED_HOST_CHECK;%s;%s\n' % (time_stamp,
															   host_name,
															   time_stamp)

	# We check for auth if it's not anonymously allowed
	check_auth()

	# Adding commands to the main queue()
	logger.debug("[WS_Nocout] command =  %s" % command)
	ext = ExternalCommand(command)
	app.from_q.put(ext)

	# OK here it's ok, it will return a 200 code


def do_downtime():
	# Getting lists of informations for the commands
	action			  = request.forms.get('action', 'add')
	time_stamp		  = request.forms.get('time_stamp', int(time.time()))
	host_name		   = request.forms.get('host_name', '')
	service_description = request.forms.get('service_description', '')
	start_time		  = request.forms.get('start_time', int(time.time()))
	end_time			= request.forms.get('end_time', int(time.time()))
	# Fixed is 1 for a period between start and end time
	fixed			   = request.forms.get('fixed', '1')
	# Fixed is 0 (flexible) for a period of duration seconds from start time
	duration			= request.forms.get('duration', int('86400'))
	trigger_id		  = request.forms.get('trigger_id', '0')
	author			  = request.forms.get('author', 'anonymous')
	comment			 = request.forms.get('comment', 'No comment')
	logger.debug("[WS_Nocout] Downtime %s - host: '%s', service: '%s', comment: '%s'" % (action, host_name, service_description, comment))

	if not host_name:
		abort(400, 'Missing parameter host_name')

	if action == 'add':
		if service_description:
			# SCHEDULE_SVC_DOWNTIME;<host_name>;<service_description>;<start_time>;<end_time>;<fixed>;<trigger_id>;<duration>;<author>;<comment>
			command = '[%s] SCHEDULE_SVC_DOWNTIME;%s;%s;%s;%s;%s;%s;%s;%s;%s\n' % ( time_stamp,
																					host_name,
																					service_description,
																					start_time,
																					end_time,
																					fixed,
																					trigger_id,
																					duration,
																					author,
																					comment
																				   )
		else:
			# SCHEDULE_HOST_DOWNTIME;<host_name>;<start_time>;<end_time>;<fixed>;<trigger_id>;<duration>;<author>;<comment>
			command = '[%s] SCHEDULE_HOST_DOWNTIME;%s;%s;%s;%s;%s;%s;%s;%s\n' % (   time_stamp,
																					host_name,
																					start_time,
																					end_time,
																					fixed,
																					trigger_id,
																					duration,
																					author,
																					comment
																				)

	if action == 'delete':
		if service_description:
			# DEL_ALL_SVC_DOWNTIMES;<host_name>;<service_description>
			command = '[%s] DEL_ALL_SVC_DOWNTIMES;%s;%s\n' % ( time_stamp,
															   host_name,
															   service_description)
		else:
			# DEL_ALL_SVC_DOWNTIMES;<host_name>
			command = '[%s] DEL_ALL_HOST_DOWNTIMES;%s\n' % ( time_stamp,
															 host_name)


	# We check for auth if it's not anonymously allowed
	if app.username != 'anonymous':
		basic = parse_auth(request.environ.get('HTTP_AUTHORIZATION', ''))
		# Maybe the user not even ask for user/pass. If so, bail out
		if not basic:
			abort(401, 'Authentication required')
		# Maybe he do not give the good credential?
		if basic[0] != app.username or basic[1] != app.password:
			abort(403, 'Authentication denied')

	# Adding commands to the main queue()
	logger.debug("[WS_Nocout] command =  %s" % command)
	ext = ExternalCommand(command)
	app.from_q.put(ext)

	# OK here it's ok, it will return a 200 code


def do_local_sync():
	""" Get the host and service config files and restart local
	check_mk instance"""

	check_auth()

	res = {
			'success': 1,
			'message': 'Config pushed successfully'
			}
	status_code = 200

	# prepare a backup of current state
	os.chdir(check_mk_conf_path)
	out = tarfile.open(check_mk_conf_path + 'wato_backup.tar.gz', mode='w:gz')
	try:
		out = prepare_tar(out)
	except Exception as exc:
		logger.error('Error in tarfile generation: {0}'.format(exc))
	finally:
		out.close()
	
	# extract files from request obj and perform check mk restart
	try:
		filename = request.files.save(check_mk_conf_path, overwrite=True)
		abs_path = check_mk_conf_path + filename
		prepare_untar(abs_path, check_mk_conf_path)
		os.system(check_mk_bin + ' -R')
	except Exception as exc:
		logger.error('Error in installing new config: {0}'.format(exc))
		# TODO: update response with error
		res.update({
			'success': 0,
			'message': 'Error with the config'
			})
		status_code = 500 
		try:
			# rollback operation
			rollback()
		except Exception as exc:
			# only for debugging purposes
			logger.error('Error in rollback operation: {0}'.format(exc))
	
	# if everything is OK
	# TODO: send response with success

	return response(body=res, status=status_code)


def prepare_untar(filename, extract_to):
	tarfile.open(filename, mode='r:gz').extractall(extract_to)


def rollback(old_tar_path):
	prepare_untar(old_tar_path, mode='r:gz').extractall(check_mk_conf_path)
	os.system(check_mk_bin + ' -R')


def prepare_tar(out):
	for entry in os.listdir('.'):
		if entry.endswith('.mk'):
			out.add(entry)

	return out


def do_live_poll():
	"""Calls live poll module"""

	check_auth()

	res = {}
	status_code = 200

	# get poll params from request obj
	try:
		req_params = request.json
	except Exception as exc:
		status_code = 500
		logger.error('[Ws-Nocout] Exception in do_live_poll: {0}'.format(
			exc))
	else:
		device_list = req_params.get('device_list')
		service_list = req_params.get('service_list')
		bs_ss_map = req_params.get(
				'bs_name_ss_mac_mapping')
		ss_map = req_params.get(
				'ss_name_mac_mapping')
		ds = req_params.get(
				'ds')
		res = live_poll_main(
				device_list=device_list,
				service_list=service_list,
				bs_name_ss_mac_mapping=bs_ss_map,
				ss_name_mac_mapping=ss_map,
				ds=ds
				)

	return response(body=res, status_code=status_code)


class WsNocout(BaseModule):
	""" Class to open an HTTP service, where a user can send
	command (e.g. restart shinken etc.)"""
	def __init__(self, modconf):
		BaseModule.__init__(self, modconf)
		try:
			logger.debug("[WS_Nocout] Configuration starting ...")
			self.username = getattr(modconf, 'username', 'anonymous')
			self.password = getattr(modconf, 'password', '')
			self.port = int(getattr(modconf, 'port', '7760'))
			self.host = getattr(modconf, 'host', '0.0.0.0')
			logger.info(
					"[WS_Nocout] Configuration done, host: %s(%s), username: %s)" %
					(self.host, self.port, self.username)
					)
		except AttributeError:
			logger.error(
					"[WS_Nocout] The module is missing a property, " 
					"check module declaration in shinken-specific.cfg"
					)
			raise
		except Exception, e:
			logger.error("[WS_Nocout] Exception : %s" % str(e))
			raise

	# We initialize the HTTP part. It's a simple wsgi backend
	# with a select hack so we can still exit if someone ask it
	def init_http(self):
		logger.info("[WS_Nocout] Starting WS arbiter http socket")
		try:
			self.srv = run(host=self.host, port=self.port, server='wsgirefselect')
		except Exception, e:
			logger.error("[WS_Nocout] Exception : %s" % str(e))
			raise

		logger.info("[WS_Nocout] Server started")
		# And we link our page
		route('/push_check_result', callback=get_page, method='POST')
		route('/restart', callback=do_restart, method='POST')
		route('/reload', callback=do_reload, method='POST')
		route('/downtime', callback=do_downtime, method='POST')
		route('/recheck', callback=do_recheck, method='POST')
		route('/local_sync', callback=do_local_sync, method='POST')
		route('/live_poll', callback=do_live_poll, method='POST')

	# When you are in "external" mode, that is the main loop of your process
	def main(self):
		global app

		# Change process name (seen in ps or top)
		self.set_proctitle(self.name)

		# It's an external module, so we need to be sure that we manage
		# the signals
		self.set_exit_handler()

		# Go for Http open :)
		self.init_http()

		# We fill the global variable with our Queue() link
		# with the arbiter, because the page should be a non-class
		# one function
		app = self

		# We will loop forever on the http socket
		input = [self.srv.socket]

		# Main blocking loop
		while not self.interrupted:
			input = [self.srv.socket]
			try:
				inputready, _, _ = select.select(input, [], [], 1)
			except select.error, e:
				logger.warning("[WS_Nocout] Exception: %s", str(e))
				continue
			for s in inputready:
				# If it's a web request, ask the webserver to do it
				if s == self.srv.socket:
					self.srv.handle_request()
