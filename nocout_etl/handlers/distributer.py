"""Module to read the data from redis broker queues
and further distribute the data to tasks in order 
to reduce load on a single worker process
"""


from celery import Task
from celery.utils.log import get_task_logger

from handlers.db_ops import RedisInterface
from start.start import app


logger = get_task_logger(__name__)
warning, error = logger.warning, logger.error

# min no of elements to be read from redis Q
READ_CAP = getattr(app.conf, 'READ_CAP', None)


class DistributeTask(Task):
	""" Task class to read data from shinken broker queue
	in chunks and call modules further"""

	ignore_result = True
	name = 'distribute-tasks'

	def run(self, *a, **kw):
		self.site_name = kw.get('site_name')
		# module to send data to
		self.mod = kw.get('module')
		try:
			self.build_export = __import__(self.mod, fromlist=['build_export'])
		except ImportError as exc:
			error('Error in importing module: {0}'.format(exc))
			raise ImportError(exc)

		# redis backed queue
		self.q_name = kw.get('Q')
		self.rds_cli = RedisInterface()
		self.q_len = self.rds_cnx.llen(self.q_name)

		return self.distribute_task()

	def distribute_task(self):
		q_len = self.q_len
		min_elems = READ_CAP if READ_CAP else 10000
		# start, end indexes for queue reads
		s, e = 0, 0
		while q_len:
			s += e
			assert min_elems != 0
			e = min(min_elems, q_len)
			data = self.rds_cli.get(s, e-1)
			if data:
				self.build_export.s(self.site_name, data).apply_async()
			q_len -= e


@app.task(name='distribute')
def caller(**opts):
	task = DistributeTask()
	task.s(**opts).apply_async()

