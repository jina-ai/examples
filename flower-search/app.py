import click
import os
import string
import random

from jina.flow import Flow

RANDOM_SEED = 13 # 5
os.environ['REPLICAS'] = str(1)
os.environ['SHARDS'] = str(1)
os.environ['TEST_WORKDIR'] = '/tmp/jina/flower'


def get_random_ws(workspace_path, length=8):
    random.seed(RANDOM_SEED)
    letters = string.ascii_lowercase
    dn = ''.join(random.choice(letters) for i in range(length))
    return os.path.join(workspace_path, dn)


def read_data(img_path, max_sample_size=10):
    if not os.path.exists(img_path):
        print('file not found: {}'.format(img_path))
    _counter = 0
    fn_list = []
    for dirs, subdirs, files in os.walk(img_path):
        for f in files:
            fn = os.path.join(img_path, f)
            if _counter >= max_sample_size:
                break
            if fn.endswith('.jpg'):
                _counter += 1
                fn_list.append(fn)
    print('indexed docs: {}'.format("\n".join(fn_list)))
    for fn in fn_list:
        yield fn.encode('utf8')


def save_topk(resp):
    for d in resp.search.docs:
        print("-" * 20)
        print("{}".format(d.raw_bytes.decode()))
        for idx, kk in enumerate(d.topk_results):
            score = kk.score.value
            if score <= 0.0:
                continue
            print('{:>2d}:({:f}):{}'.format(
                idx, score, kk.match_doc.raw_bytes.decode()))


@click.command()
@click.option('--task', '-t')
@click.option('--num_docs', '-n', default=50)
@click.option('--top_k', '-k', default=5)
def main(task, num_docs, top_k):
    workspace_path = '/tmp/jina/urbandict'
    os.environ['TMP_WORKSPACE'] = get_random_ws(workspace_path)
    data_path = os.path.join(os.environ['TEST_WORKDIR'], 'jpg')
    if task == 'index':
        flow = Flow().load_config('flow-index.yml')
        with flow.build() as fl:
            fl.index(raw_bytes=read_data(data_path, num_docs), batch_size=10)
        print('done')
    elif task == 'query':
        flow = Flow().load_config('flow-query.yml')
        with flow.build() as fl:
            ppr = lambda x: save_topk(x)
            fl.search(read_data(data_path, 10), callback=ppr, topk=top_k)
    else:
        raise NotImplementedError(
            f'unknown task: {task}. A valid task is either `index` or `query`.')


if __name__ == '__main__':
    main()