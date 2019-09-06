import time
import pytest
from nameko.rpc import rpc
from nameko.exceptions import deserialize_to_instance, RpcTimeout
from nameko.containers import ServiceContainer

from nameko_proxy import StandaloneRpcProxy


CONFIG = {
    'AMQP_URI': 'pyamqp://guest:guest@127.0.0.1'
}


@deserialize_to_instance
class FooTestError(Exception):
    pass


class FooService(object):
    name = 'foo_service'

    @rpc
    def test(self, val):
        return val

    @rpc
    def error(self, msg):
        raise FooTestError(msg)

    @rpc
    def sleep(self, seconds=0):
        time.sleep(seconds)
        return seconds


def test_rpc_proxy():
    container = ServiceContainer(FooService, CONFIG)
    container.start()

    with StandaloneRpcProxy(CONFIG) as proxy:
        assert proxy.foo_service.test("test") == "test"

        msg = "Error occurred"
        try:
            proxy.foo_service.error(msg)
        except FooTestError as error:
            assert str(error) == msg


def test_async_calls():
    container = ServiceContainer(FooService, CONFIG)
    container.start()

    with StandaloneRpcProxy(CONFIG) as proxy:
        resp1 = proxy.foo_service.test.call_async(1)
        resp2 = proxy.foo_service.sleep.call_async(2)
        resp3 = proxy.foo_service.test.call_async(3)
        resp4 = proxy.foo_service.test.call_async(4)
        resp5 = proxy.foo_service.test.call_async(5)
        assert resp2.result() == 2
        assert resp3.result() == 3
        assert resp1.result() == 1
        assert resp4.result() == 4
        assert resp5.result() == 5


def test_rpc_timeout():
    container = ServiceContainer(FooService, CONFIG)
    container.start()

    with StandaloneRpcProxy(CONFIG, timeout=.5) as proxy:
        with pytest.raises(RpcTimeout):
            assert proxy.foo_service.sleep(1)

        assert proxy.foo_service.sleep(0) == 0
