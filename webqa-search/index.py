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

    for item in result[:1000]:
        yield item
def main():
    workspace_path = '/tmp/jina/webqa'
    os.environ['TMP_WORKSPACE'] = workspace_path
    data_fn = os.path.join(workspace_path, "web_text_zh_valid.json")
    flow = Flow().add(
        name='answer_extractor', yaml_path='images/answer-extractor/answer_extractor.yml'
    ).add(
        name='answer_meta_doc_indexer', yaml_path='images/answer-meta-doc-indexer/answer_meta_doc_indexer.yml', recv_from='answer_extractor'
    ).add(
        name='answer_encoder', yaml_path='images/encoder/encoder.yml', recv_from="answer_extractor", timeout_ready=60000, replicas=2
    ).add(
        name='answer_chunk_indexer', yaml_path='images/answer-chunk-indexer/answer_chunk_indexer.yml', recv_from='answer_encoder'
    ).add(
        name='answer_meta_chunk_indexer', yaml_path='images/answer-meta-chunk-indexer/answer_meta_chunk_indexer.yml', recv_from='answer_chunk_indexer'
    ).add(
        name='title_extractor', yaml_path='images/title-extractor/title_extractor.yml', recv_from='gateway'
    ).add(
        name='title_encoder', yaml_path='images/encoder/encoder.yml', recv_from='title_extractor', timeout_ready=60000, replicas=1
    ).add(
        name='title_chunk_indexer', yaml_path='images/title-chunk-indexer/title_chunk_indexer.yml', recv_from='title_encoder'
    ).add(
        name='title_meta_chunk_indexer', yaml_path='images/title-meta-chunk-indexer/title_meta_chunk_indexer.yml',
        recv_from='title_chunk_indexer'
    ).add(
        name='merge', yaml_path='images/merger/merger.yml',
        recv_from=['answer_meta_chunk_indexer', 'answer_meta_doc_indexer', 'title_meta_chunk_indexer']
    )
    with flow.build() as f:
        f.index(raw_bytes=read_data(data_fn))

if __name__ == '__main__':
    main()


