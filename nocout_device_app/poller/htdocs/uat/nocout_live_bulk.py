'''
nocout_live_bulk.py
===================

Script that fetches current data for a list of services running
on a set of devices
'''
from wato import *
from pprint import pformat
import os
from multiprocessing import Process, Queue
from ast import literal_eval
#import Queue
from nocout_live import get_current_value, nocout_log
from itertools import groupby
from operator import itemgetter
from nocout import get_parent
import signal
from subprocess import Popen, PIPE
from threading import Timer
#import multiprocessing
import time
import pexpect
import mysql.connector
import requests
logger = nocout_log()

def main():
    """
    Entry point for all the functions

    Returns:
        {
	 "success": 1,
	 "message": "Data fetched successfully",
	 "error_message": None,
	 "value": [] # The current values for the desired service data sources
	}
    """
    logger.info('[Polling Iteration Start_b]')
    response = {
        "success": 1,
        "message": "Data fetched successfully",
        "error_message": None,
        "value": []
    }
    action = ''
    action = html.var('mode')
    if action == 'live':
        response['value'] = poll_device()

    elif action == 'ping_test':
        ping_conf_get()
	


    else:
        response.update({
            "message": "No data",
            "error_message": "No action defined for this case"
        })

    html.write(pformat(response))



def ping_test_mail_sent(id):
	try:
		#url = 'https://121.244.255.107/escalation/email/'   # for prod
		url = 'https://10.133.12.182/download_center/processedreportemail/' #API URL to send the email
		data1 = {'pk' : id, 'report_type' : 'ping'}
		r = requests.post(url, data = data1, verify=False)
		if r.status_code == 200:
			logger.info("Email-sent")
	except Exception as e :
		logger.error('in ping e-mail sent: ' + pformat(e))





def ping_status_update(id,file_name):   # The function change the status(0 to 1) pending to success on db
	try:
		db = mysql.connector.connect(
			user='root',
			password='TAta12#$',
			host='10.133.12.182',
			port='3600',
			db='nocout_dev'
							)
		cur = db.cursor()
		file_path = "/omd/tmp/media/download_excels/"+file_name
		data_values = ('1',file_path,id)
		table = "performance_pingstabilitytest"
		query = "UPDATE `%s` " % table
		query += "SET `status`=%s,`file_path`=%s WHERE `id`=%s"
		cur.execute(query, data_values)
		db.commit()
	except Exception as e :
		logger.error('in ping status: ' + pformat(e))
	finally :
		cur.close()
		db.close()
	


def ping_file_send(file_name):
	try:
		#hostname = " tmadmin@121.244.255.107:"   # for production

		SSH_NEWKEY = r'Are you sure you want to continue connecting \(yes/no\)\?'
		hostname = " tmadmin@10.133.12.182:"
		remote_path = "/omd/tmp/media/download_excels/"
		cmd = "scp -P 5522 "+file_name+hostname+remote_path
		child = pexpect.spawn(cmd)
		i = child.expect( [ pexpect.TIMEOUT, SSH_NEWKEY, pexpect.EOF])
		if i == 1:
			child.sendline('yes')
	                child.expect("password:",timeout=120)
        	        child.sendline('TTpl12#$')   #   password
                	child.expect(pexpect.EOF, timeout=10)
                	logger.info('file sent' )  

		else:

			child.expect("password:",timeout=120)
			child.sendline('TTpl12#$')   #   password
			child.expect(pexpect.EOF, timeout=10)
			logger.info('file sent' )  

	except Exception as e:
		logger.error('in ping file sending: ' + pformat(e))   # change with the looger




def ping1(id, ip, time1):   
	try :
		child = Popen(['ping', ip], stdin=PIPE, stdout=PIPE, stderr=PIPE)
		Timer(time1, child.send_signal, [signal.SIGINT]).start()  # like ctrl+c to process after time time
		out, err = child.communicate() 
		find1 = out.find("statistics")   # index value of statitics 
	
		str1 = ("--- %s ping statistics ---" %(ip))
		time2 = time.time()
		# to give the name to file use epoch + ip_address
		epoch_time = int(time2)
		file_name1 = ip+"_"+str(epoch_time)
		file_path = "/omd/ping_test/"    # own system path where file will be stored
		file_name = file_path+file_name1
		file_txt = open(file_name, "w")
		file_txt.write(str1)
		file_txt.write(out[find1+14:])
		file_txt.close()
		logger.info(pformat(str1))
		str2=   out[find1+14:]
		logger.info(pformat(str2))
		ping_file_send(file_name)
		ping_status_update(id,file_name1)
		time.sleep(8)
		ping_test_mail_sent(id)
		#print(err.decode())
	except Exception as e :	
		logger.error('in ping1: ' + pformat(e))


#Ping statbility function start from here
#make sure /omd/ping_test/  folder on the poller.

def ping_conf_get():
	logger.info("ping started")
	list1 = literal_eval(html.var('data'))
	#logger.info(list1)
	
	for each in list1:
		try:
			ip= each.get("ip_address")
			id= each.get("id")
			time1 = int(each.get("time_interval"))
			#time1 = time1*3600
			process = Process(target=ping1, args=(id,ip, time1))  # call ping1 function with arguments
			process.start()
		except Exception as e :
			logger.error('in ping_conf_get: ' + pformat(e))
	








def poll_device():
	response = []
	wimax_service_list = ['wimax_dl_cinr','wimax_ul_cinr','wimax_dl_rssi','wimax_ul_rssi','wimax_ul_intrf','wimax_dl_intrf',
	'wimax_modulation_dl_fec','wimax_modulation_ul_fec']
	try:
		logger.info('[Polling Iteration Start]')
		device_list = literal_eval(html.var('device_list'))
		service_list = literal_eval(html.var('service_list'))
		bs_name_ss_mac_mapping = literal_eval(html.var('bs_name_ss_mac_mapping'))
		ss_name_mac_mapping = literal_eval(html.var('ss_name_mac_mapping'))
		is_first_call = literal_eval(html.var('is_first_call'))
	except Exception as e:
		logger.info('excep: ' + pformat(e))
	logger.info('device_list : %s and service_list : %s' % (device_list, service_list))
	# If in case no `ds` supplied in req obj, [''] would be supplied as default
	try:
		data_source_list = literal_eval(html.var('ds'))
	except Exception:
		data_source_list = ['']
		#logger.error('No ds provided in request object', exc_info=True)
	if not data_source_list:
		data_source_list = ['']
	logger.debug('data_source_list : %s' % data_source_list)

	#current_values = get_current_value(device, service, data_source_list)

		#t = threading.Thread(
		#		target=get_current_value,
		#		args=(q,),
		#		kwargs=
		#		{
		#			'device': device,
		#			'service_list': service_list,
		#			'data_source_list': data_source_list
		#			}
		#		)
		###t.daemon =True
		#t.start()

	q = Queue()
	jobs = [
			Process(
				target=get_current_value,
				args=(q,),
				kwargs=
				{
					'device': device,
					'service_list': service_list,
					'data_source_list': data_source_list,
					'bs_name_ss_mac_mapping': bs_name_ss_mac_mapping,
					'ss_name_mac_mapping': ss_name_mac_mapping,
					'is_first_call': is_first_call
					}
				) for device in device_list
			]
	for j in jobs:
	        j.start()
	for k in jobs:
	        k.join()

	##logger.debug('Queue ' + pformat(q.qsize()))
	while True:
		if not q.empty():
			response.append(q.get())
		else:
			break
	logger.info('[Polling Iteration End]')
	logger.debug('Queue ' + pformat(response))

	return response


def poll_processes():
	logger.debug('Parent Process ID: ' + pformat(os.getppid()))
	logger.debug('Process ID: ' + pformat(os.getpid()))

