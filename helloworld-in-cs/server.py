__copyright__ = "Copyright (c) 2020 Jina AI Limited. All rights reserved."
__license__ = "Apache-2.0"

import os
import threading

from jina.flow import Flow
from jina.logging import default_logger
from jina.main.parser import set_hw_parser
from pkg_resources import resource_filename
from jina.helloworld.components import *


def hello_world(args):
    # this envs are referred in index and query flow YAMLs
    os.environ['RESOURCE_DIR'] = resource_filename('jina', 'resources')
    os.environ['SHARDS'] = str(args.shards)
    os.environ['PARALLEL'] = str(args.parallel)
    os.environ['HW_WORKDIR'] = args.workdir
    os.environ['WITH_LOGSERVER'] = str(args.logserver)

    # reduce the network load by using `fp16`, or even `uint8`
    os.environ['JINA_ARRAY_QUANT'] = 'fp16'

    # now comes the real work
    # load index flow from a YAML file

    f = Flow.load_config(args.index_uses)
    # run it!
    with f:
        default_logger.success(f'hello-world server is started at {f.host}:{f.port_expose}, '
                               f'you can now use "python client.py --port-expose {f.port_expose} --host {f.host}" to send request!')
        f.block()


if __name__ == '__main__':
    p = set_hw_parser()
    p.add_argument('--index-uses', required=True, type=str, help='the yaml path of the index flow')
    p.add_argument('--shards', type=int, default=1, help='number of shards when index and query')
    p.add_argument('--parallel', type=int, default=1, help='number of parallel when index and query')
    #p.add_argument('--workdir', type=str, default='localhost', help='the address hello-world server')
    #p.add_argument('--logserver', type=str, default='localhost', help='start a log server for the dashboard')
    p.add_argument('--host', type=str, default='localhost', help='the address hello-world server')
    p.add_argument('--port_expose', type=int, default=51328, help='the grpc port of the hello-world server')
    hello_world(p.parse_args())