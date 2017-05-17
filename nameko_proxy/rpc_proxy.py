from nameko.standalone.rpc import ClusterProxy, StandaloneProxyBase
from nameko.containers import WorkerContext

from .reply_listener import StandaloneReplyListener, THREADING_MODE

__all__ = ['ClusterRpcProxy']


class _StandaloneProxyBase(StandaloneProxyBase):

    def __init__(self, config, context_data=None, timeout=None,
                 async_mode=THREADING_MODE, worker_ctx_cls=WorkerContext,
                 reply_listener_cls=StandaloneReplyListener):
        super().__init__(
            config, context_data, timeout, reply_listener_cls)

        container = self.ServiceContainer(config)

        self._worker_ctx = worker_ctx_cls(
            container, service=None, entrypoint=self.Dummy, data=context_data)
        self._reply_listener = reply_listener_cls(
            timeout=timeout, async_mode=async_mode).bind(container)


class ClusterRpcProxy(_StandaloneProxyBase):
    def __init__(self, *args, **kwargs):
        super(ClusterRpcProxy, self).__init__(*args, **kwargs)
        self._proxy = ClusterProxy(self._worker_ctx, self._reply_listener)
