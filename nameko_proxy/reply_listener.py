from nameko.rpc import ReplyListener

from nameko_proxy.queue_consumer import QueueConsumer

from nameko_proxy.event_queue import EventQueue

__all__ = ['StandaloneReplyListener']


class StandaloneReplyListener(ReplyListener):

    queue_consumer = None

    def __init__(self, timeout=None):
        self.queue_consumer = QueueConsumer(timeout)
        super(StandaloneReplyListener, self).__init__()

    def get_reply_event(self, correlation_id):
        reply_event = EventQueue()
        self._reply_events[correlation_id] = reply_event
        return reply_event
