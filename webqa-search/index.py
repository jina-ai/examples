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
    data_fn = os.path.join(workspace_path, "web_text_zh_valid.json")
    flow = Flow().add(
        name='answer_extractor', yaml_path='images/answer_extractor/answer_extractor.yml'
    ).add(
        name='answer_encoder', yaml_path='images/encoder/encoder.yml', needs="answer_extractor", timeout_ready=60000
    ).add(
        name='answer_meta_doc_indexer', yaml_path='images/answer_meta_doc_indexer/answer_meta_doc_indexer.yml',
        needs='answer_extractor'
    ).add(
        name='answer_compound_chunk_indexer',
        yaml_path='images/answer_compound_chunk_indexer/answer_compound_chunk_indexer.yml', needs='answer_encoder'
    ).add(
        name='title_extractor', yaml_path='images/title_extractor/title_extractor.yml', needs='gateway'
    ).add(
        name='title_encoder', yaml_path='images/encoder/encoder.yml', needs='title_extractor', timeout_ready=60000,
        replicas=1
    ).add(
        name='title_compound_chunk_indexer',
        yaml_path='images/title_compound_chunk_indexer/title_compound_chunk_indexer.yml', needs='title_encoder'
    ).add(
        name='merge', yaml_path='images/merger/merger.yml',
        needs=['title_compound_chunk_indexer', 'answer_meta_doc_indexer', 'answer_compound_chunk_indexer']
    )
    with flow.build() as f:
        f.index(raw_bytes=read_data(data_fn))

if __name__ == '__main__':
    main()


