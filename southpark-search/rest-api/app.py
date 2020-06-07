__copyright__ = "Copyright (c) 2020 Jina AI Limited. All rights reserved."
__license__ = "Apache-2.0"

import sys
import os

from jina.flow import Flow


# def print_topk(resp, word):
#     for d in resp.search.docs:
#         print(f'Ta-Dah🔮, here are what we found for: {word}')
#         for idx, kk in enumerate(d.topk_results):
#             score = kk.score.value
#             if score < 0.0:
#                 continue
#             doc = kk.match_doc.text
#             name, line = doc.split('!', maxsplit=1)
#             print('> {:>2d}({:.2f}). {} said, "{}"'.format(idx, score, name.upper(), line.strip()))


# def read_query_data(text):
#     yield '{}'.format(text).lower()


def config(mode='index'):
    os.environ['REPLICAS'] = str(2) if mode == 'index' else str(1)
    os.environ['SHARDS'] = str(8)
    os.environ['TMP_WORKSPACE'] = './workspace'
    os.environ['TMP_DATA_DIR'] = './data'
    os.environ['JINA_PORT'] = os.environ.get('JINA_PORT', str(45678))


def print_error():
    print('USAGE: python app.py [index|search]')


def index():
    data_path = os.path.join(os.environ['TMP_DATA_DIR'], 'character-lines.csv')
    f = Flow().load_config('flow-index.yml')
    with f:
        f.index_lines(filepath=data_path, batch_size=8)


def search():
    f = Flow().load_config('flow-query.yml')
    with f:
        f.block()


def dryrun():
    f = Flow().load_config('flow-index.yml')
    with f:
        f.dry_run()


def main():
    if len(sys.argv) < 2:
        print_error()
        exit(1)
    config(sys.argv[1])
    if sys.argv[1] == 'index':
        index()
    elif sys.argv[1] == 'search':
        search()
    elif sys.argv[1] == 'dryrun':
        dryrun()
    else:
        print_error()
        raise NotImplementedError(f'unsupported mode {sys.argv[1]}')

    # os.environ['TMP_WORKSPACE'] = get_random_ws(os.environ['TMP_DATA_DIR'])
    # data_path = os.path.join(os.environ['TMP_DATA_DIR'], 'character-lines.csv')
    # if task == 'index':
    #     f = Flow().load_config('flow-index.yml')
    #     with f:
    #         f.index_lines(filepath=data_path, size=num_docs, batch_size=8)
    #     print('done')
    # elif task == 'query':
    #     f = Flow().load_config('flow-query.yml')
    #     with f:
    #         while True:
    #             text = input('please type a sentence: ')
    #             if not text:
    #                 break
    #             ppr = lambda x: print_topk(x, text)
    #             f.search(read_query_data(text), callback=ppr, topk=top_k)
    # else:
    #     raise NotImplementedError(
    #         f'unknown task: {task}. A valid task is either `index` or `query`.')


if __name__ == '__main__':
    main()
