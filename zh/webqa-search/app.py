__copyright__ = "Copyright (c) 2020 Jina AI Limited. All rights reserved."
__license__ = "Apache-2.0"

import json
import os
import random

import click
from jina.flow import Flow

workspace_path = '/tmp/jina/webqa/'

os.environ['TMP_WORKSPACE'] = workspace_path


def read_data(fn, num_docs):
    with open(os.path.join(workspace_path, fn), 'r', encoding='utf-8') as f:
        items = json.load(f)
    result = []
    random.seed(0)
    for _, value in items.items():
        result.append("{}".format(json.dumps(value, ensure_ascii=False)))
    if num_docs > 0:
        random.shuffle(result)
        result = result[:num_docs]
    for item in result:
        print(item)
        yield item


def print_topk(resp):
    print(f'以下是相似的问题:')
    for d in resp.search.docs:
        for tk in d.topk_results:
            item = json.loads(tk.match_doc.text)
            print('👉%s' % item['title'])


def read_query_data(item):
    yield "{}".format(json.dumps(item, ensure_ascii=False))


@click.command()
@click.option('--task', '-t', default='query')
@click.option('--top_k', '-k', default=5)
@click.option('--num_docs', '-n', default=100)
def main(task, top_k, num_docs):
    if task == 'index':
        data_fn = os.path.join(workspace_path, "pre_web_text_zh_valid.json")
        flow = Flow().load_config('flow-index.yml')
        with flow:
            # flow.index_lines(lines=read_data(data_fn, num_docs), batch_size=32)
            flow.index_lines(filepath=data_fn, size=num_docs, batch_size=32)


    elif task == 'query':
        flow = Flow().load_config('flow-query.yml')
        with flow:
            while True:
                title = input('请输入问题: ')
                item = {'title': title}
                if not title:
                    break
                ppr = lambda x: print_topk(x)
                flow.search(read_query_data(item), output_fn=ppr, topk=top_k)
    else:
        raise NotImplementedError(
            f'unknown task: {task}. A valid task is either `index` or `query`.')


if __name__ == '__main__':
    main()
