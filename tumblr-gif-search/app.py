import glob
import json
import os
import random
from datetime import datetime

from google.protobuf.json_format import MessageToDict
from jina.flow import Flow

RUN_MODE = 'debug-index'
MODEL_ID = '20200202224053'

WORK_DIR = '/Volumes/TOSHIBA-4T/model/'
GIF_BLOB = '/Volumes/TOSHIBA-4T/dataset/thumblr-gif-data/*.gif'  # 'data/*.gif'
TIMESTAMP = datetime.now().strftime('%Y%m%d%H%M%S')

os.environ['TEST_WORKDIR'] = WORK_DIR + MODEL_ID
os.environ['GNES_LOG_FORMAT'] = 'JSON'
os.environ['REPLICAS'] = '3'
# os.environ['GRPC_VERBOSITY'] = 'debug'
# os.environ['GRPC_TRACE']='tcp'
do_index = True

if RUN_MODE == 'debug-index':
    replicas = 1
    num_docs = 1000
elif RUN_MODE == 'index':
    replicas = 4
    num_docs = 200000
elif RUN_MODE == 'debug-query' or RUN_MODE == 'query':
    do_index = False
    replicas = 1
    num_docs = 10
else:
    raise AttributeError(RUN_MODE)

if RUN_MODE.endswith('index'):
    os.environ['TEST_WORKDIR'] = WORK_DIR + TIMESTAMP
    os.makedirs(os.environ['TEST_WORKDIR'], exist_ok=True)


def print_result(resp, fp):
    for d in resp.search.docs:
        v = MessageToDict(d, including_default_value_fields=True)
        v['metaInfo'] = d.raw_bytes.decode()
        for k, kk in zip(v['topkResults'], d.topk_results):
            k['matchDoc']['metaInfo'] = kk.match_doc.raw_bytes.decode()
            # k['score']['explained'] = json.loads(kk.score.explained)
        fp.write(json.dumps(v, sort_keys=True) + '\n')


if do_index:
    # index
    f = Flow.load_config('flow-index.yml')

    bytes_gen = (g.encode() for g in glob.glob(GIF_BLOB)[:num_docs])

    with f.build() as fl:
        fl.index(bytes_gen, batch_size=64)
else:
    # query
    q = Flow.load_config('flow-query.yml')

    with open(os.environ['TEST_WORKDIR'] + '/topk.json', 'w', encoding='utf8') as fp:
        ppr = lambda x: print_result(x, fp)

        if RUN_MODE == 'query':
            bytes_gen = (g.encode() for g in random.sample(glob.glob(GIF_BLOB), num_docs))
        else:
            bytes_gen = (g.encode() for g in glob.glob(GIF_BLOB)[:num_docs])
        with q.build(backend='process') as fl:
            fl.search(bytes_gen, callback=ppr, top_k=60, batch_size=32)
