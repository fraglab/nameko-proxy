# nameko-proxy
Standalone async proxy to communicate with Nameko services.

Motivation: Communicate with Nameko from standalone application with minimum real connections 
and asynchronous queue consumer to support multi threading.

# Installation

Install latest version from Git:
```bash
pip install git+https://github.com/fraglab/nameko-proxy.git
```

# Usage

Nameko-proxy provide ClusterRpcProxy the same interface as Nameko:

```python
from nameko_proxy import ClusterRpcProxy

config = {
    'AMQP_URI': "pyamqp://guest:guest@localhost"
}

with ClusterRpcProxy(config) as rpc:
    rpc.<SERVICE_NAME>.<METHOD_NAME>()
```

# Wrappers

## Flask

### Configuration

Wrapper get from flask config all parameters started from "NAMEKO_" and pass it to ClusterRpcProxy.


* NAMEKO_AMQP_URI (**mandatory**) - specify amqp uri to nameko
* NAMEKO_RPC_TIMEOUT - specify nameko rpc timeout
* NAMEKO_PREFETCH_COUNT


### Example

```python
from eventlet import monkey_patch
from flask import Flask, g
from nameko_proxy.wrappers.flask import FlaskNamekoProxy


def make_app(conf_path: str='settings.py') -> Flask:
    app = Flask(__name__)
    app.config.from_pyfile(conf_path)
    return app
    
    
def start_app():
    app = make_app()

    monkey_patch()
    with app.app_context():
        g.rpc = FlaskNamekoProxy(app)
        app.run()
        
 
if __name__ == '__main__':
    start_app()
```