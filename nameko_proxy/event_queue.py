from nameko.exceptions import RpcTimeout
from queue import Queue, Empty

class EventQueue(Queue):

    def __init__(self, timeout=None, *args, **kwargs):
        self.timeout = timeout
        super(EventQueue, self).__init__(*args, **kwargs)

    def send_exception(self, arg):
        self.put({'result': None, 'exc': arg})

    def send(self, result=None, exc=None):
        self.put({'result': result, 'exc': exc})

    def wait(self, timeout=None):
        timeout = timeout if timeout is not None else self.timeout
        try:
            res = self.get(timeout=timeout)
            if res['exc']:
                raise res['exc']
            return res['result']
        except Empty:
            raise RpcTimeout(timeout)
    def ready(self):
        return not self.empty()

