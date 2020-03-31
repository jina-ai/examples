
import json
import os

from google.protobuf.json_format import MessageToDict

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
    data_fn = os.path.join(workspace_path, "web_text_zh_train0.json")
    flow = Flow().add(
        name='extractor', yaml_path='yaml/title_extractor.yml', recv_from='gateway'
    ).add(
        name='encoder', yaml_path='yaml/encoder.yml', recv_from="extractor", timeout_ready=60000, replicas=3
    ).add(
        name='title_chunk_indexer', yaml_path='yaml/title_chunk_indexer.yml', recv_from='encoder'
    ).add(
        name='title_meta_chunk_indexer', yaml_path='yaml/title_meta_chunk_indexer.yml', recv_from='title_chunk_indexer'
    ).add(
        name='answer_chunk_indexer', yaml_path='yaml/answer_chunk_indexer.yml', recv_from='encoder'
    ).add(
        name='answer_meta_chunk_indexer', yaml_path='yaml/answer_meta_chunk_indexer.yml', recv_from='answer_chunk_indexer'
    ).add(
        name='merge', yaml_path='yaml/merger.yml', recv_from=['answer_meta_chunk_indexer', 'title_meta_chunk_indexer']
    ).add(
        name='ranker', yaml_path='yaml/ranker.yml', recv_from='merge'
    ).add(
        name='answer_meta_doc_indexer', yaml_path='yaml/answer_meta_doc_indexer.yml', recv_from='ranker'
    )

    def print_topk(resp, fp):
        for d in resp.search.docs:
            v = MessageToDict(d, including_default_value_fields=True)
            v['metaInfo'] = d.raw_bytes.decode()
            for k, kk in zip(v['topkResults'], d.topk_results):
                k['matchDoc']['metaInfo'] = kk.match_doc.raw_bytes.decode()
            fp.write(json.dumps(v, sort_keys=True, indent=4)+"\n")
    with open("{}/query_result.json".format(os.environ['TMP_WORKSPACE']), "w") as fp:
        with flow.build() as f:
            pr = lambda x: print_topk(x, fp)
            f.search(raw_bytes=read_data(data_fn), callback=pr)

if __name__ == '__main__':
    main()