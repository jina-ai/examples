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
    os.environ['REPLICAS'] = str(args.replicas)
    os.environ['HW_WORKDIR'] = args.workdir
    os.environ['WITH_LOGSERVER'] = str(args.logserver)

    # reduce the network load by using `fp16`, or even `uint8`
    os.environ['JINA_ARRAY_QUANT'] = 'fp16'

    # now comes the real work
    # load index flow from a YAML file

    f = Flow.load_config(args.index_yaml_path)
    # run it!
    with f:
        default_logger.success(f'hello-world server is started at {f.host}:{f.port_grpc}, '
                               f'you can now use "python client.py --port-grpc {f.port_grpc} --host {f.host}" to send request!')
        threading.Event().wait()


if __name__ == '__main__':
    hello_world(set_hw_parser().parse_args())