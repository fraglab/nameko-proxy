from logging import getLogger

from flask import _app_ctx_stack as stack

from nameko_proxy import StandaloneRpcProxy

logger = getLogger()


class FlaskNamekoProxy:

    context_data = None
    context_data_hooks = []
    config = None

    def __init__(self, app=None):
        if app:
            self.init_app(app)

    def init_app(self, app, context_data=None):
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

    def register_context_hook(self, func: callable):
        self.context_data_hooks.append(func)

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
                nameko_proxy = StandaloneRpcProxy(
                    self.config,
                    context_data=self.context_data,
                    timeout=self.config.get('RPC_TIMEOUT', None),
                )
                for hook in self.context_data_hooks:
                    nameko_proxy.register_context_hook(hook)
                ctx.nameko_proxy = nameko_proxy
        return ctx.nameko_proxy
