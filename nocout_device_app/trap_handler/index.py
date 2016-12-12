#!/usr/bin/env python
# -*- coding: utf-8 -*-

import web
from manual_ticketing import manual_ticketing_main
import logging

logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s %(levelname)s %(message)s',
                    filename='/apps/nocout_etl/manual_ticketing.log')

urls = ("/.*", "hello")
app = web.application(urls, globals())
class hello:
    def GET(self):
        return 'Hello, world!'
    def POST(self):
	logging.info('Request for manual ticketing received')
	logging.info(web.data())
	try:
	    #man_tic_obj = manual_ticketing()
            manual_ticketing_main(eval(web.data()))
	    #man_tic_obj.manual_ticketing_main()
	except Exception as e:
	    logging.info('index file log')
	    logging.info(e)

	logging.info('Ticket sent')
        return 'self.request.POST'

if __name__ == "__main__":
    web.wsgi.runwsgi = lambda func, addr=None: web.wsgi.runfcgi(func, addr)
    app.run()
