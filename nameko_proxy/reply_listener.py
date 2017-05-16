from nameko.rpc import ReplyListener

from .queue_consumer import QueueConsumer

__all__ = ['StandaloneReplyListener']


THREADING_MODE = 'threading'
EVENTLET_MODE = 'eventlet'


class UnknownAsyncMode(Exception):
    pass


def _import(async_mode):
    if async_mode == THREADING_MODE:
        from threading import Thread, Event

        def spawn(func_):
            thread = Thread(target=func_)
            thread.daemon = True
            thread.start()
            return thread

        class EventCls(Event):
            _result = None
            _exc = None

            def send(self, result=None, exc=None):
                self._result = result
                if exc is not None and not isinstance(exc, tuple):
                    exc = (exc, )
                self._exc = exc

                self.set()

            def send_exception(self, *args):
                return self.send(None, args)

    elif async_mode == EVENTLET_MODE:
        from eventlet import spawn
        from eventlet.event import Event as EventCls
    else:
        raise UnknownAsyncMode("Unknown async mode: %s" % async_mode)

    return spawn, EventCls


class StandaloneReplyListener(ReplyListener):

    queue_consumer = None

    def __init__(self, timeout=None, async_mode="threading"):
        spawn_cls, self.event_cls = _import(async_mode)
        self.queue_consumer = QueueConsumer(spawn_cls, timeout=timeout)
        super(StandaloneReplyListener, self).__init__()

    def stop(self):
        self.queue_consumer.unregister_provider(self)
        super(ReplyListener, self).stop()

    def get_reply_event(self, correlation_id):
        reply_event = self.event_cls()
        self._reply_events[correlation_id] = reply_event
        return reply_event
