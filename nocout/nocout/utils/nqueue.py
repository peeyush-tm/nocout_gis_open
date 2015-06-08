# nqueue is nocout cache implmentation
# based on REDIS & Django-Redis & Python Redis
# would provide dropin replacement for QUEUE python

try:
    import cPickle as pickle
except ImportError:
    import pickle

from django.conf import settings

from redis import StrictRedis

class NQueue(object):
    """
    nqueue class for nocout
    """
    def __init__(self, qconf=None, qname='nocout', serializer=pickle):
        """The default connection parameters are: host='localhost', port=6379, db=0"""

        self._settings = getattr(settings, 'QUEUES', {})
        print(self._settings)
        self._params = self._settings.get(
            qconf,
            self._settings.get(
                'default', {
                    'protocol': 'redis',
                    'host': 'localhost',
                    'port': 6379,
                    'db': 0
                }
            )
        )
        # TODO: Support all the configuration parameters for REDIS
        self._timeout = self._params.get('TIMEOUT', 60)
        self._url = self._params.get('LOCATION',
                                     '{protocol}://{host}:{port}/{db}'.format(**self._params)
                                     )
        self._namespace = self._params.get('NAMESPACE', 'noc:queue:')

        self.serializer = serializer
        self.qkey = '%s:%s' % (self._namespace, qname)

        self.__redis = StrictRedis.from_url(self._url)

    def __len__(self):
        return self.__redis.llen(self.qkey)

    @property
    def key(self):
        """Return the key name used to store this queue in Redis."""
        return self.qkey

    def clear(self):
        """Clear the queue of all messages, deleting the Redis key."""
        self.__redis.delete(self.key)

    def qsize(self):
        """Return the approximate size of the queue."""
        return self.__len__()

    def empty(self):
        """Return True if the queue is empty, False otherwise."""
        return True if self.qsize() == 0 else False

    def get(self, block=True, timeout=None):
        """Return a message from the queue. Example:

        :param block: whether or not to wait until a msg is available in
            the queue before returning; ``False`` by default
        :param timeout: when using :attr:`block`, if no msg is available
            for :attr:`timeout` in seconds, give up and return ``None``
        """
        if block:
            if timeout is None:
                timeout = 0
            msg = self.__redis.blpop(self.key, timeout=timeout)
            if msg is not None:
                msg = msg[1]
        else:
            msg = self.__redis.lpop(self.key)
        if msg is not None and self.serializer is not None:
            msg = self.serializer.loads(msg)
        return msg

    def put(self, *msgs):
        """Put one or more messages onto the queue. Example:

        To put messages onto the queue in bulk, which can be significantly
        faster if you have a large number of messages:

        """
        if self.serializer is not None:
            msgs = map(self.serializer.dumps, msgs)
        self.__redis.rpush(self.key, *msgs)

    def get_nowait(self):
        """Equivalent to get(False)."""
        return self.get(False)
