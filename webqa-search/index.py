import json
import os

from jina.flow import Flow


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

    for item in result[:50000]:
        yield item


def main():
    workspace_path = '/home/cally/jina/webqa'
    os.environ['TMP_WORKSPACE'] = workspace_path
    data_fn = os.path.join(workspace_path, "web_text_zh_train.json")
    flow = (Flow().add(name='title_extractor', yaml_path='images/title_extractor/title_extractor.yml')
            .add(name='tmd_indexer', yaml_path='images/title_meta_doc_indexer/title_meta_doc_indexer.yml',
                 needs='gateway')
            .add(name='title_encoder', yaml_path='images/encoder/encoder.yml', needs='title_extractor',
                 timeout_ready=60000, replicas=3)
            .add(name='tcc_indexer', yaml_path='images/title_compound_chunk_indexer/title_compound_chunk_indexer.yml',
                 needs='title_encoder')
            .join(['tcc_indexer', 'tmd_indexer']))
    with flow.build() as f:
        f.index(raw_bytes=read_data(data_fn))


if __name__ == '__main__':
    main()
