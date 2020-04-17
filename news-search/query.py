import json
import os

from google.protobuf.json_format import MessageToDict
from jina.flow import Flow


def read_data(fn):
    contents = []
    with open(fn, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.replace('\n', '')
            item = json.loads(line)
            content = item['content']
            if content == '':
                continue

            contents.append({'content': content})

    result = []
    for content in contents:
        result.append(("{}".format(json.dumps(content, ensure_ascii=False))).encode("utf-8"))

    for item in result[:10]:
        yield item


def main():
    workspace_path = '/home/cally/jina/news'
    os.environ['TMP_WORKSPACE'] = workspace_path
    data_fn = os.path.join(workspace_path, "news2016zh_valid.json")
    flow = (Flow().add(name='extractor', yaml_path='images/extractor/extractor.yml')
            .add(name='encoder', yaml_path='images/encoder/encoder.yml', needs='extractor', timeout_ready=60000,
                 replicas=2)
            .add(name='compound_chunk_indexer', yaml_path='images/compound_chunk_indexer/compound_chunk_indexer.yml',
                 needs='encoder', timeout_ready=60000)
            .add(name='ranker', yaml_path='images/ranker/ranker.yml', needs='compound_chunk_indexer')
            .add(name='meta_doc_indexer', yaml_path='images/meta_doc_indexer/meta_doc_indexer.yml', needs='ranker'))

    def print_topk(resp, fp):
        for d in resp.search.docs:
            v = MessageToDict(d, including_default_value_fields=True)
            v['metaInfo'] = d.raw_bytes.decode()
            for k, kk in zip(v['topkResults'], d.topk_results):
                k['matchDoc']['metaInfo'] = kk.match_doc.raw_bytes.decode()
            fp.write(json.dumps(v, sort_keys=True, indent=4, ensure_ascii=False) + "\n")

    with open("{}/query_result.json".format(os.environ['TMP_WORKSPACE']), "w") as fp:
        with flow.build() as f:
            pr = lambda x: print_topk(x, fp)
            f.search(raw_bytes=read_data(data_fn), callback=pr, top_k=3)


if __name__ == '__main__':
    main()
