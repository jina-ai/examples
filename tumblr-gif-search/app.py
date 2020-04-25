__copyright__ = "Copyright (c) 2020 Jina AI Limited. All rights reserved."
__license__ = "Apache-2.0"


import glob
import json
import os
from datetime import datetime

from google.protobuf.json_format import MessageToDict

os.environ['JINA_LOG_PROFILING'] = 'true'

from jina.flow import Flow

RUN_MODE = 'index'
MODEL_ID = '20200424191102'

WORK_DIR = '/Volumes/TOSHIBA-4T/model/'
GIF_BLOB = '/Volumes/TOSHIBA-4T/dataset/thumblr-gif-data/*.gif'  # 'data/*.gif'
TIMESTAMP = datetime.now().strftime('%Y%m%d%H%M%S')

os.environ['TEST_WORKDIR'] = WORK_DIR + MODEL_ID
# os.environ['JINA_LOG_FILE'] = 'JSON'
os.environ['JINA_LOG_PROFILING'] = 'true'
# os.environ['JINA_LOG_VERBOSITY'] = 'DEBUG'
# os.environ['GRPC_VERBOSITY'] = 'debug'
# os.environ['GRPC_TRACE']='tcp'
do_index = True

shards = 8

if RUN_MODE == 'debug-index':
    replicas = 2
    num_docs = 10000
elif RUN_MODE == 'index':
    replicas = 3
    num_docs = 200000
elif RUN_MODE == 'debug-query' or RUN_MODE == 'query':
    do_index = False
    replicas = 1
    num_docs = 100
else:
    raise AttributeError(RUN_MODE)

os.environ['REPLICAS'] = str(replicas)
os.environ['SHARDS'] = str(shards)

if RUN_MODE.endswith('index'):
    os.environ['TEST_WORKDIR'] = WORK_DIR + TIMESTAMP
    os.makedirs(os.environ['TEST_WORKDIR'], exist_ok=True)


def print_result(resp, fp):
    for d in resp.search.docs:
        v = MessageToDict(d, including_default_value_fields=True)
        v['metaInfo'] = d.meta_info.decode()
        for k, kk in zip(v['topkResults'], d.topk_results):
            k['matchDoc']['metaInfo'] = kk.match_doc.meta_info.decode()
            # k['score']['explained'] = json.loads(kk.score.explained)
        fp.write(json.dumps(v, sort_keys=True) + '\n')


def input_fn(random=False, with_filename=True):
    idx = 0
    for g in glob.glob(GIF_BLOB)[:num_docs]:
        with open(g, 'rb') as fp:
            # print(f'im asking to read {idx}')
            if with_filename:
                yield g.encode() + b'JINA_DELIM' + fp.read()
            else:
                yield fp.read()
            idx += 1


if do_index:
    # index
    f = Flow.load_config('flow-index.yml')

    # input_fn = (g.encode() for g in glob.glob(GIF_BLOB)[:num_docs])

    with f:
        f.index(input_fn, batch_size=8)
else:
    # query
    q = Flow.load_config('flow-query.yml')

    with open(os.environ['TEST_WORKDIR'] + '/topk.json', 'w', encoding='utf8') as fp:
        ppr = lambda x: print_result(x, fp)

        if RUN_MODE == 'query':
            bytes_gen = input_fn(random=True)
        else:
            bytes_gen = input_fn
        with q:
            q.search(bytes_gen, callback=ppr, top_k=80, batch_size=8)
