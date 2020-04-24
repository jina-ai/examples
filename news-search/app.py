import json
import os

import click
from jina.flow import Flow

workspace_path = '/tmp/jina/news/'

os.environ['TMP_WORKSPACE'] = workspace_path

def read_data(fn):
    items = []
    with open(fn, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.replace('\n', '')
            item = json.loads(line)
            content = item['content']
            if content == '':
                continue

            items.append({'content': content})

    results = []
    for content in items:
        results.append(("{}".format(json.dumps(content, ensure_ascii=False))).encode("utf-8"))

    for item in results[:100]:
        yield item


def print_topk(resp):
    print(f'以下是相似的新闻内容:')
    for d in resp.search.docs:
        for tk in d.topk_results:
            item = json.loads(tk.match_doc.raw_bytes.decode('utf-8'))
            print('→%s' % item['content'])

def read_query_data(item):
    yield ("{}".format(json.dumps(item, ensure_ascii=False))).encode('utf-8')

@click.command()
@click.option('--task', '-t', default='index')
@click.option('--top_k', '-k', default=5)
def main(task, top_k):
    if task == 'index':
        data_fn = os.path.join(workspace_path, "news2016zh_valid.json")
        flow = Flow().load_config('flow-index.yml')
        with flow.build() as fl:
            fl.index(raw_bytes=read_data(data_fn), batch_size=32)

    elif task == 'query':
        flow = Flow().load_config('flow-query.yml')
        with flow.build() as fl:
            while True:
                content = input('请输入新闻内容: ')
                if not content:
                    break
                item = {'content': content}

                ppr = lambda x: print_topk(x)
                fl.search(read_query_data(item), callback=ppr, topk=top_k)
    else:
        raise NotImplementedError(
            f'unknown task: {task}. A valid task is either `index` or `query`.')

if __name__ == '__main__':
    main()