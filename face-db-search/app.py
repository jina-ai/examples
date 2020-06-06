__copyright__ = "Copyright (c) 2020 Jina AI Limited. All rights reserved."
__license__ = "Apache-2.0"


import click
import os
import string
import random
import sys

from jina.flow import Flow

RANDOM_SEED = 42
os.environ['REPLICAS'] = str(1)
os.environ['SHARDS'] = str(1)
os.environ['TMP_DATA_DIR'] = '/tmp/jina/celeb'
os.environ['COLOR_CHANNEL_AXIS'] = str(0)


def get_random_ws(workspace_path, length=8):
    random.seed(RANDOM_SEED)
    letters = string.ascii_lowercase
    dn = ''.join(random.choice(letters) for i in range(length))
    return os.path.join(workspace_path, dn)

def read_custom_data(img_path, max_sample_size=-1):
    if not os.path.exists(img_path):
        raise FileNotFoundError('file not found: {}'.format(img_path))

    fn_list = []
    if os.path.isdir(img_path):
        path_join_fn = lambda d, f: os.path.join(d, f)
        fn_list = [ path_join_fn(img_path, f) for f in os.listdir(img_path) if os.path.isfile(path_join_fn(img_path, f)) and f.endswith('.jpg') ]
    elif os.path.isfile(img_path):
        if img_path.endswith('.jpg'):
            fn_list.append(img_path)
    else:
        raise FileNotFoundError('{} must be a file or directory.'.format(img_path));

    if not fn_list:
        raise FileNotFoundError('No .jpg file or files to query, path: {}'.format(img_path));

    if max_sample_size > 0:
        random.shuffle(fn_list)
        fn_list = fn_list[:max_sample_size]

    for fn in fn_list:
        yield fn.encode('utf8')

def read_data(img_path, max_sample_size=-1):
    if not os.path.exists(img_path):
        raise FileNotFoundError('file not found: {}'.format(img_path))
    fn_list = []
    for dirs, subdirs, files in os.walk(img_path):
        for f in files:
            fn = os.path.join(dirs, f)
            if fn.endswith('.jpg'):
                fn_list.append(fn)
    if max_sample_size > 0:
        random.shuffle(fn_list)
        fn_list = fn_list[:max_sample_size]
    for fn in fn_list:
        yield fn.encode('utf8')


def save_topk(resp, output_fn=None):
    results = []
    for d in resp.search.docs:
        cur_result = []
        d_fn = d.meta_info.decode()
        cur_result.append(d_fn)
        print("-" * 20)
        print(f'query image: {d_fn}')
        print('matched images' + "*" * 10)
        print("{}".format(d.buffer.decode()))
        for idx, kk in enumerate(d.topk_results):
            score = kk.score.value
            if score < 0.0:
                continue
            m_fn = kk.match_doc.buffer.decode()
            print('{:>2d}:({:f}):{}'.format(
                idx, score, m_fn))
            cur_result.append(m_fn)
        results.append(cur_result)
    if output_fn is not None:
        import matplotlib.pyplot as plt
        import matplotlib.image as mpimg
        top_k = max([len(r) for r in results])
        num_q = len(resp.search.docs)
        f, ax = plt.subplots(num_q, top_k, figsize=(8, 20), squeeze=False)
        for q_idx, r in enumerate(results):
            for m_idx, img in enumerate(r):
                fname = os.path.split(img)[-1]
                names=fname.split('_')[:-1]
                fname=''.join(names)
                fname = f'' if m_idx == 0 else f'top_{m_idx}: {fname}'
                ax[q_idx][m_idx].imshow(mpimg.imread(img))
                ax[q_idx][m_idx].set_title(fname, fontsize=7)
        [aa.axis('off') for a in ax for aa in a]
        plt.tight_layout()
        plt.savefig(output_fn)


@click.command()
@click.option('--task', '-t')
@click.option('--num_docs', '-n', default=500)
@click.option('--top_k', '-k', default=5)
@click.option('--path', '-p', help='Specify a JPG file or directory to query', default='')
def main(task, num_docs, top_k, path):
    from jina.clients.python import PyClient
    os.environ['TMP_WORKSPACE'] = get_random_ws(os.environ['TMP_DATA_DIR'])
    data_path = os.path.join(os.environ['TMP_DATA_DIR'], 'lfw')
    if task == 'index':
        flow = Flow().load_config('flow-index.yml')
        with flow.build() as fl:
            print('Checking Input...')
            PyClient.check_input(read_data(data_path, num_docs))
            print('Start Indexing...')
            fl.index(buffer=read_data(data_path, num_docs), batch_size=4)
    elif task == 'query':
        if not path:
            cmd_prompt = '\033[{}mpython {} -t query -p <JPG file or directory>\033[0m'.format(32, sys.argv[0])
            prompt = input(f'You can specify a JPG file or directory you own to query: {cmd_prompt}\nDo you want? Please input y or n: ')
            if prompt and prompt == 'y':
               sys.exit(0)

        read_data_fn = read_custom_data if path else read_data
        if path:
            data_path = path

        flow = Flow().load_config('flow-query.yml')
        with flow.build() as fl:
            ppr = lambda x: save_topk(x, os.path.join(os.environ['TMP_DATA_DIR'], 'query_results.png'))
            fl.search(read_data_fn(data_path, 5), callback=ppr, top_k=top_k)
    else:
        raise NotImplementedError(
            f'unknown task: {task}. A valid task is either `index` or `query`.')


if __name__ == '__main__':
    main()

