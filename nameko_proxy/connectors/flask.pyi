from flask import Flask

from nameko.standalone.rpc import ClusterProxy, ServiceProxy, WorkerContext
from nameko_proxy.rpc_proxy import ClusterRpcProxy


class FlaskNamekoProxy:

    config = ...  # type: dict

    @property
    def nameko_rpc_timeout(self) -> float:
        return

    def init_app(self, app: Flask, async_mode: str='', context_data: dict=None, worker_cls: WorkerContext=None):
        pass

    def __getattr__(self, name) -> ServiceProxy:
        return

    def get_connection(self) -> ClusterProxy:
        return

    @staticmethod
    def get_proxy() -> ClusterRpcProxy:
        return

    def _teardown_nameko_connection(self, _):
        pass

    def disconnect(self):
        pass
