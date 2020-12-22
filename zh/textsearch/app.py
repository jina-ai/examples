__copyright__ = "Copyright (c) 2020 Jina AI Limited. All rights reserved."
__license__ = "Apache-2.0"

import os
import json
import click
from jina.flow import Flow


def conf():
    # workspace_path = 'WORKSPACE-KBERT'
    workspace_path = 'WORKSPACE-1000test'

    os.environ['TMP_WORKSPACE'] = workspace_path
    os.environ["JINA_PORT"] = os.environ.get("JINA_PORT", str(45678))


def print_topk(resp, sentence):
    for d in resp.search.docs:
        print(f"Ta-Dah🔮, here are what we found for: {sentence}")
        for idx, match in enumerate(d.matches):

            score = match.score.value
            if score < 0.0:
                continue
            content = match.text.strip()

            # if "樱桃" in content:
            #     print("查询匹配结果：  ", score, content)
            # if "甜品" in content or "佐料" in content or "奶油" in content:
            #     print("查询匹配结果：  ", score, content)
            print("查询匹配结果：  ", score, content)


def read_query_data(item):
    yield "{}".format(json.dumps(item, ensure_ascii=False))


def dryrun():
    f = Flow().load_config("flow-index.yml")
    with f:
        f.dry_run()


@click.command()
@click.option('--task', '-t', default='query')
@click.option('--top_k', '-k', default=25)
@click.option('--num_docs', '-n', default=1000)
def main(task, top_k, num_docs):
    conf()
    if task == 'index':
        data_fn = 'test.jsonl'
        flow = Flow().load_config('flow-index.yml')
        with flow:
            flow.index_lines(filepath=data_fn, size=num_docs, batch_size=100)


    elif task == 'query':
        flow = Flow().load_config('flow-query.yml')
        # flow.use_rest_gateway()
        with flow:
            # flow.block()

            while True:
                content = input('请输入问题: ')
                item = {'content': content}
                if not content:
                    break

                def ppr(x):
                    print_topk(x, content)
                    # print_topk2(x)

                # flow.search(content, output_fn=ppr, top_k=top_k)
                flow.search(read_query_data(item), output_fn=ppr, top_k=top_k)
    else:
        raise NotImplementedError(
            f'unknown task: {task}. A valid task is either `index` or `query`.')


if __name__ == '__main__':
    main()
