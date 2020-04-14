import json
import os

from jina.flow import Flow


def read_data(fn):
    items = []
    with open(fn, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.replace('\n', '')
            item = json.loads(line)
            content = item['content']
            if content == '':
                continue

            items.append(item)

    results = []
    for content in items:
        results.append(("{}".format(json.dumps(content, ensure_ascii=False))).encode("utf-8"))

    for item in results[:5000]:
        yield item
def main():
    workspace_path = '/home/cally/jina/news'
    os.environ['TMP_WORKSPACE'] = workspace_path
    data_fn = os.path.join(workspace_path, "news2016zh_valid.json")
    flow = Flow().add(
        name='extractor', yaml_path='images/extractor/extractor.yml'
    ).add(
        name='meta_doc_indexer', yaml_path='images/meta_doc_indexer/meta_doc_indexer.yml',
        needs='gateway'
    ).add(
        name='encoder', yaml_path='images/encoder/encoder.yml', needs='extractor', timeout_ready=600000, replicas=1
    ).add(
        name='compound_chunk_indexer',
        yaml_path='images/compound_chunk_indexer/compound_chunk_indexer.yml', needs='encoder'
    ).add(
        name='merge', yaml_path='images/merger/merger.yml',
        needs=['compound_chunk_indexer', 'meta_doc_indexer']
    )
    with flow.build() as f:
        f.index(raw_bytes=read_data(data_fn))

if __name__ == '__main__':
    main()