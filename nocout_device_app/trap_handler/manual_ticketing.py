from start.start import app
import correlation
#from correlation import correlation
import logging

logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s %(levelname)s %(message)s',
                    filename='/apps/nocout_etl/manual_ticketing.log')

try:
    urls = ("/.*", "manual_ticketing")
    app = web.application(urls, globals())
except Exception, e:
    pass


def manual_ticketing_main(alarm):
    try:
        correlation.manual_ticketing_main.s(alarm).apply_async()
    except Exception as e:
        logging.info(e)
        logging.info('In manual ticketing file')


if __name__ == '__main__':
    alarm = {'ip_address':'10.132.180.10', 'alarm_name': 'Device_not_reachable', 'severity': 'critical', 'traptime':"2016-12-05 11:50:58" }
    manual_ticketing_main(alarm)
