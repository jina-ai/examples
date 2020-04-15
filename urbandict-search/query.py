import os
from google.protobuf.json_format import MessageToDict
import json

from jina.flow import Flow
from index import read_data


def main():
    workspace_path = '/tmp/jina/urbandict'
    os.environ['TMP_WORKSPACE'] = workspace_path
    data_fn = os.path.join(workspace_path, "query.csv")
    read_data(data_fn)

    flow = (Flow().add(
        name='extractor', yaml_path='yaml/extractor.yml'
    ).add(
        name='encoder', yaml_path='yaml/encoder.yml'
    ).add(
        name='compound_chunk_indexer', yaml_path='yaml/compound_chunk_indexer.yml'
    ).add(
        name='ranker', yaml_path='yaml/ranker.yml'
    ).add(
        name='meta_doc_indexer', yaml_path='yaml/meta_doc_indexer.yml'
    ))

    def print_topk(resp, fp):
        for d in resp.search.docs:
            v = MessageToDict(d, including_default_value_fields=True)
            v['metaInfo'] = d.raw_bytes.decode()
            for k, kk in zip(v['topkResults'], d.topk_results):
                k['matchDoc']['metaInfo'] = kk.match_doc.raw_bytes.decode()
            fp.write(json.dumps(v, sort_keys=True, indent=4)+"\n")

    with open("{}/query_result.json".format(os.environ['TMP_WORKSPACE']), "w") as fp:
        with flow.build() as f:
            ppr = lambda x: print_topk(x, fp)
            f.search(read_data(data_fn, 10), callback=ppr)


if __name__ == '__main__':
    main()
