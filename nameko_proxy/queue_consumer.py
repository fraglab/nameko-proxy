from logging import getLogger

import eventlet
from eventlet import event
import threading
from nameko_proxy.event_queue import EventQueue
from kombu import Connection
from kombu.messaging import Consumer
from kombu.mixins import ConsumerMixin
from nameko.constants import (
    AMQP_URI_CONFIG_KEY, DEFAULT_SERIALIZER, SERIALIZER_CONFIG_KEY,
    HEARTBEAT_CONFIG_KEY, DEFAULT_HEARTBEAT, TRANSPORT_OPTIONS_CONFIG_KEY,
    DEFAULT_TRANSPORT_OPTIONS, AMQP_SSL_CONFIG_KEY
)

logger = getLogger()


class QueueConsumer(ConsumerMixin):

    PREFETCH_COUNT_CONFIG_KEY = 'PREFETCH_COUNT'
    DEFAULT_KOMBU_PREFETCH_COUNT = 10

    def __init__(self, timeout=None):
        self.timeout = timeout

        self.provider = None
        self.queue = None
        self.prefetch_count = None
        self.serializer = None
        self.accept = []

        self._managed_threads = []
        self._consumers_ready = EventQueue()
        self._connection = None
        self._thread = None

    @property
    def amqp_uri(self):
        return self.provider.container.config[AMQP_URI_CONFIG_KEY]

    @property
    def connection(self):
        if not self._connection:
            heartbeat = self.provider.container.config.get(
                HEARTBEAT_CONFIG_KEY, DEFAULT_HEARTBEAT
            )
            transport_options = self.provider.container.config.get(
                TRANSPORT_OPTIONS_CONFIG_KEY, DEFAULT_TRANSPORT_OPTIONS
            )
            ssl = self.provider.container.config.get(AMQP_SSL_CONFIG_KEY)
            self._connection = Connection(self.amqp_uri,
                                          transport_options=transport_options,
                                          heartbeat=heartbeat,
                                          ssl=ssl
                                         )
        return self._connection

    def register_provider(self, provider):
        logger.debug("QueueConsumer registering: %s", provider)
        self.provider = provider
        self.queue = provider.queue
        self.serializer = provider.container.config.get(SERIALIZER_CONFIG_KEY, DEFAULT_SERIALIZER)
        self.prefetch_count = self.provider.container.config.get(
            self.PREFETCH_COUNT_CONFIG_KEY, self.DEFAULT_KOMBU_PREFETCH_COUNT)
        self.accept = [self.serializer]

        self.start()

    def start(self):
        self._thread = threading.Thread(target=self._handle_thread)
        self._thread.daemon = True
        self._thread.start()
        self._consumers_ready.wait()

    def _handle_thread(self):
        logger.info("QueueConsumer starting...")
        try:
            self.run()
        except Exception as error:
            logger.error("Managed thread end with error: %s", error)

            if not self._consumers_ready.ready():
                self._consumers_ready.send_exception(error)

    def on_consume_ready(self, connection, channel, consumers, **kwargs):
        if not self._consumers_ready.ready():
            self._consumers_ready.send(None)

    def on_connection_error(self, exc, interval):
        logger.warning(
            "Error connecting to broker at {} ({}).\n"
            "Retrying in {} seconds.".format(self.amqp_uri, exc, interval))

    def unregister_provider(self, _):
        if self._connection:
            self.connection.close()
        self.should_stop = True

    def get_consumers(self, _, channel):
        consumer = Consumer(channel, queues=[self.provider.queue], accept=self.accept,
                            no_ack=False, callbacks=[self.provider.handle_message])
        consumer.qos(prefetch_count=self.prefetch_count)
        return [consumer]

    @staticmethod
    def ack_message(msg):
        msg.ack()
