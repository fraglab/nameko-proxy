from queue import Queue

class EventQueue(Queue):

    def send_exception(self, arg):
        self.put({'result': None, 'exc': arg})

    def send(self, result=None, exc=None):
        self.put({'result': result, 'exc': exc})

    def wait(self, timeout=None):
        res = self.get(timeout=timeout)
        if res['exc']:
            raise res['exc']
        return res['result']

    def ready(self):
        return not self.empty()

