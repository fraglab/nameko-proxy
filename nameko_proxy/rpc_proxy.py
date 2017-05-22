from logging import getLogger

from nameko.standalone.rpc import ClusterProxy, StandaloneProxyBase
from nameko.containers import WorkerContext

from nameko_proxy.reply_listener import StandaloneReplyListener

__all__ = ['ClusterRpcProxy']

logger = getLogger()


class _StandaloneProxyBase(StandaloneProxyBase):

    def __init__(self, config, context_data=None, timeout=None,
                 worker_ctx_cls=WorkerContext,
                 reply_listener_cls=StandaloneReplyListener):
        try:
            super().__init__(
                config, context_data, timeout, worker_ctx_cls, reply_listener_cls)
        except TypeError:
            logger.warning("Nameko >= 2.6.0 had deprecated redefine worker_ctx_cls.")
            super().__init__(
                config, context_data, timeout, reply_listener_cls)

        container = self.ServiceContainer(config)

        self._worker_ctx = worker_ctx_cls(
            container, service=None, entrypoint=self.Dummy, data=context_data)
        self._reply_listener = reply_listener_cls(
            timeout=timeout).bind(container)


class ClusterRpcProxy(_StandaloneProxyBase):
    def __init__(self, *args, **kwargs):
        super(ClusterRpcProxy, self).__init__(*args, **kwargs)
        self._proxy = ClusterProxy(self._worker_ctx, self._reply_listener)
