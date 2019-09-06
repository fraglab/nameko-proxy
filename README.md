# nameko-proxy
Standalone async proxy to communicate with Nameko services.

Motivation: Communicate with Nameko from standalone application with minimum real connections 
and asynchronous queue consumer to support multi threading.

# Installation

Install
```bash
pip3 install nameko-proxy
```

Install latest version from Git:
```bash
pip install git+https://github.com/fraglab/nameko-proxy.git
```

# Usage

Nameko-proxy provide StandaloneRpcProxy the same interface as Nameko ClusterRpcProxy:

```python
from nameko_proxy import StandaloneRpcProxy

config = {
    'AMQP_URI': "pyamqp://guest:guest@localhost"
}

with StandaloneRpcProxy(config) as rpc:
    rpc.SERVICE_NAME.METHOD_NAME()
    
    response = rpc.SERVICE_NAME.METHOD_NAME.call_async()
    print(response.result())
```

# Wrappers

## Flask

### Configuration

Wrapper get from flask config all parameters started from prefix "NAMEKO_" and pass it to ClusterRpcProxy.


* NAMEKO_AMQP_URI (**mandatory**) - specify amqp uri to nameko.
* NAMEKO_RPC_TIMEOUT - (default: None) specify nameko rpc timeout.
* NAMEKO_PREFETCH_COUNT - (default: 10) kombu consumer will set the prefetch_count QoS value at startup. <br>
(Details: docs.celeryproject.org/projects/kombu/en/latest/userguide/consumers.html)
* NAMEKO_<NAMEKO CONF PARAMETER> - any nameko config parameter can be pass through flask settings.

### Example

```python
from flask import Flask
from nameko_proxy.wrappers.flask_wrapper import FlaskNamekoProxy


rpc = FlaskNamekoProxy()


def make_app():
    app = Flask(__name__)
    app.config.update(dict(
        NAMEKO_AMQP_URI='pyamqp://guest:guest@localhost'
    ))
    rpc.init_app(app)
    return app

app = make_app()

if __name__ == '__main__':
    app.run()
```


### Context Data Hook

StandaloneRpcProxy provide mechanism to change context_data dynamical per request. 
It useful if you want for example add to each request unique request_id for better logging.

```python
from flask import Flask, request
from nameko_proxy.wrappers.flask_wrapper import FlaskNamekoProxy
from nameko.constants import CALL_ID_STACK_CONTEXT_KEY

app = Flask(__name__)
rpc = FlaskNamekoProxy(app)
rpc.register_context_hook(lambda: {CALL_ID_STACK_CONTEXT_KEY: getattr(request, 'request_id')})  # Hook function must return dict object.
```
