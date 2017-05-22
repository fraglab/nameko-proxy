from logging import getLogger

from flask import _app_ctx_stack as stack
from nameko.containers import WorkerContext

from nameko_proxy.rpc_proxy import ClusterRpcProxy

logger = getLogger()


class FlaskNamekoProxy:

    worker_cls = None
    context_data = None
    config = None

    def __init__(self, app=None):
        if app:
            self.init_app(app)

    def init_app(self, app, context_data=None, worker_cls=WorkerContext):
        self.worker_cls = worker_cls
        self.context_data = context_data
        self.config = {key[len('NAMEKO_'):]: val for key, val in app.config.items() if key.startswith('NAMEKO_')}

        app.teardown_appcontext(self._teardown_nameko_connection)

    def _teardown_nameko_connection(self, _):
        self.disconnect()

    @staticmethod
    def disconnect():
        ctx = stack.top
        if hasattr(ctx, 'nameko_proxy'):
            logger.info("Nameko rpc proxy disconnecting...")
            ctx.nameko_proxy.stop()

    def __getattr__(self, name):
        return getattr(self.connection, name)

    @property
    def connection(self):
        ctx = stack.top
        if ctx is not None:
            if not hasattr(ctx, 'nameko_connection'):
                ctx.nameko_connection = self.proxy.start()
        return ctx.nameko_connection

    @property
    def proxy(self):
        ctx = stack.top
        if ctx is not None:
            if not hasattr(ctx, 'nameko_proxy'):
                ctx.nameko_proxy = ClusterRpcProxy(
                    self.config,
                    context_data=self.context_data,
                    timeout=self.config.get('RPC_TIMEOUT', None),
                    worker_ctx_cls=self.worker_cls,
                )
        return ctx.nameko_proxy
