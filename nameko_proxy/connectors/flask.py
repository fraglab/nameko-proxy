from logging import getLogger

from flask import g

from nameko_proxy.rpc_proxy import ClusterRpcProxy
from nameko_proxy.reply_listener import THREADING_MODE

logger = getLogger()


class FlaskNamekoProxy:

    def __init__(self, app=None, context_data=None, worker_cls=None):
        self.config = None
        if app:
            self.init_app(app, context_data, worker_cls)

    def init_app(self, app, async_mode=THREADING_MODE, context_data=None, worker_cls=None):
        self.config = {key[len('NAMEKO_'):]: val for key, val in app.config.items() if key.startswith('NAMEKO_')}
        g._nameko_rpc_proxy = ClusterRpcProxy(
            self.config,
            async_mode=async_mode,
            context_data=context_data,
            timeout=self.nameko_rpc_timeout,
            worker_ctx_cls=worker_cls,
        )
        app.teardown_appcontext(self._teardown_nameko_connection)

    @property
    def nameko_rpc_timeout(self):
        return self.config.get('RPC_TIMEOUT', None)

    def __getattr__(self, name):
        return getattr(self.get_connection(), name)

    def get_connection(self):
        connection = getattr(g, '_nameko_connection', None)
        if not connection:
            connection = self.get_proxy().start()
            g._nameko_connection = connection
        return connection

    @staticmethod
    def get_proxy():
        return getattr(g, '_nameko_rpc_proxy', None)

    def _teardown_nameko_connection(self, _):
        self.disconnect()

    def __del__(self):
        self.disconnect()

    def disconnect(self):
        if self.get_proxy():
            logger.info("Nameko rpc proxy disconnecting...")
            self.get_proxy().stop()
