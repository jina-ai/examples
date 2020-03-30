
import json
import os
from jina.flow import Flow

def read_data(fn='/tmp/jina/webqa/web_text_zh_valid.json'):
    items = {}
    with open(fn, 'r', encoding='utf-8') as f:
        for line in f:
            item = json.loads(line)
            if item['content'] == '':
                continue
            if item['qid'] not in items.keys():
                items[item['qid']] = {}
                items[item['qid']]['title'] = item['title']
                items[item['qid']]['answers'] = [{'answer_id': item['answer_id'], 'content': item['content']}]
            else:
                items[item['qid']]['answers'].append({'answer_id': item['answer_id'], 'content': item['content']})

    result = []
    for qid, value in items.items():
        value['qid'] = qid
        result.append(("{}".format(json.dumps(value, ensure_ascii=False))).encode("utf-8"))

    for item in result[:100]:
        yield item

def main():
    workspace_path = '/tmp/jina/webqa'
    os.environ['TMP_WORKSPACE'] = workspace_path
    data_fn = os.path.join(workspace_path, "web_text_zh_train0.json")
    flow = Flow().add(
        name='extractor', yaml_path='yaml/title_extractor.yml', recv_from='gateway'
    ).add(
        name='encoder', yaml_path='yaml/encoder.yml', recv_from="extractor", timeout_ready=60000
    ).add(
        name='title_chunk_indexer', yaml_path='yaml/title_chunk_indexer.yml', recv_from='encoder'
    ).add(
        name='title_meta_chunk_indexer', yaml_path='yaml/title_meta_chunk_indexer.yml', recv_from='title_chunk_indexer'
    ).add(
        name='title_ranker', yaml_path='yaml/title_ranker.yml', recv_from='title_meta_chunk_indexer'
    )
    with flow.build() as f:
        f.search(raw_bytes=read_data(data_fn))

if __name__ == '__main__':
    main()