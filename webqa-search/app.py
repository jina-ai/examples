
import json
import os

import click
from jina.flow import Flow

workspace_path = '/tmp/jina/webqa/'

os.environ['TMP_WORKSPACE'] = workspace_path

def read_data(fn):
    items = {}
    with open(fn, 'r', encoding='utf-8') as f:
        for line in f:
            item = json.loads(line)
            if item['content'] == '':
                continue
            if item['qid'] not in items.keys():
                items[item['qid']] = {}
                items[item['qid']]['title'] = item['title']
                items[item['qid']]['answers'] = [{'content': item['content']}]
            else:
                items[item['qid']]['answers'].append({'content': item['content']})

    result = []
    for _, value in items.items():
        result.append(("{}".format(json.dumps(value, ensure_ascii=False))).encode("utf-8"))

    for item in result[:100]:
        yield item

def print_topk(resp):
    print(f'以下是相似的问题:')
    for d in resp.search.docs:
        for tk in d.topk_results:
            item = json.loads(tk.match_doc.raw_bytes.decode('utf-8'))
            print('→%s' % item['title'])

def read_query_data(item):
    yield ("{}".format(json.dumps(item, ensure_ascii=False))).encode('utf-8')

@click.command()
@click.option('--task', '-t', default='query')
@click.option('--top_k', '-k', default=5)
def main(task, top_k):
    if task == 'index':
        data_fn = os.path.join(workspace_path, "web_text_zh_train.json")
        flow = Flow().load_config('flow-index.yml')
        with flow.build() as fl:
            fl.index(raw_bytes=read_data(data_fn), batch_size=4)

    elif task == 'query':
        flow = Flow().load_config('flow-query.yml')
        with flow.build() as fl:
            while True:
                title = input('请输入问题: ')
                item = {'title': title}
                if not title:
                    break
                ppr = lambda x: print_topk(x)
                fl.search(read_query_data(item), callback=ppr, topk=top_k)
    else:
        raise NotImplementedError(
            f'unknown task: {task}. A valid task is either `index` or `query`.')

if __name__ == '__main__':
    main()