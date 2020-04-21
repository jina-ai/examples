import click
import json
import os
import string
import random
from google.protobuf.json_format import MessageToDict

from jina.flow import Flow
from jina.enums import FlowOptimizeLevel

RANDOM_SEED = 5  # 3
os.environ['REPLICAS'] = str(1)
os.environ['SHARDS'] = str(1)


def get_random_ws(workspace_path, length=8):
    random.seed(RANDOM_SEED)
    letters = string.ascii_lowercase
    dn = ''.join(random.choice(letters) for i in range(length))
    return os.path.join(workspace_path, dn)


def read_data(fn, max_sample_size=1000):
    with open(fn, 'r') as f:
        data_dict = json.load(f)
        for r in data_dict[:max_sample_size]:
            yield '{}'.format(json.dumps(r, ensure_ascii=False)).encode('utf8')


def print_topk(resp):
    for d in resp.search.docs:
        v = MessageToDict(d, including_default_value_fields=True)
        word = json.loads(d.meta_info.decode('utf8'))['text']
        print(f'Ta-Dah🔮, here are what we found for: {word}')
        for idx, (k, kk) in enumerate(zip(v['topkResults'], d.topk_results)):
            score = k["score"]["value"]
            if score <= 0.0:
                continue
            print('{:>2d}:({:f}):{}'.format(
                idx, score, kk.match_doc.raw_bytes.decode()
            ))


def read_query_data(text):
    result = []
    json_dict = {"word": '', 'text': text, 'weight': 1.0}
    result.append(("{}".format(json.dumps(json_dict, ensure_ascii=False))).encode("utf8"))
    for r in result:
        yield r


@click.command()
@click.option('--task', '-t')
@click.option('--num_docs', '-n', default=50)
@click.option('--top_k', '-k', default=5)
def main(task, num_docs, top_k):
    workspace_path = '/tmp/jina/urbandict'
    os.environ['TMP_WORKSPACE'] = get_random_ws(workspace_path)
    print(f'{os.environ["TMP_WORKSPACE"]}')
    data_fn = os.path.join('/tmp/jina/urbandict', "urbandict-word-defs.json")
    if task == 'index':
        flow = Flow().load_config('flow-index.yml')
        flow.optimize_level = FlowOptimizeLevel.IGNORE_GATEWAY
        with flow.build() as fl:
            fl.index(raw_bytes=read_data(data_fn, num_docs), batch_size=16)
    elif task == 'query':
        flow = Flow().load_config('flow-query.yml')
        with flow.build() as fl:
            ppr = lambda x: print_topk(x)
            while True:
                text = input('word definition: ')
                if not text:
                    break
                fl.search(read_query_data(text), callback=ppr, topk=top_k)
    else:
        raise NotImplementedError(f'unknown task: {task}. A valid task is either `index` or `query`.')


if __name__ == '__main__':
    main()
