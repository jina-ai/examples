__copyright__ = "Copyright (c) 2020 Jina AI Limited. All rights reserved."
__license__ = "Apache-2.0"

import os
import numpy as np
from pathlib import Path

from jina.clients import py_client
from jina.helloworld.helper import load_mnist, download_data
from jina.main.parser import set_hw_parser


def input_fn(fp, index=True, num_doc=None):
    img_data = load_mnist(fp)
    if not index:
        # shuffle for random query
        img_data = np.take(img_data, np.random.permutation(img_data.shape[0]), axis=0)
    d_id = 0
    for r in img_data:
        yield r.tobytes()
        d_id += 1
        if num_doc is not None and d_id > num_doc:
            break

def hello_world(args):
    Path(args.workdir).mkdir(parents=True, exist_ok=True)

    targets = {
        'index': {
            'url': args.index_data_url,
            'filename': os.path.join(args.workdir, 'index-original')
        },
        'query': {
            'url': args.query_data_url,
            'filename': os.path.join(args.workdir, 'query-original')
        }
    }

    # download the data
    download_data(targets)

    # run it!
    py_client(port_expose=args.port_expose, host=args.host).index(
        input_fn(targets['index']['filename']), batch_size=args.index_batch_size)


if __name__ == '__main__':
    p = set_hw_parser()
    p.add_argument('--port-expose', required=True, type=int, help='the grpc port of the hello-world server')
    p.add_argument('--host', type=str, default='localhost', help='the address hello-world server')
    hello_world(p.parse_args())
