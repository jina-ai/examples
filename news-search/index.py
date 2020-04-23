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

            items.append({'content': content})

    results = []
    for content in items:
        results.append(("{}".format(json.dumps(content, ensure_ascii=False))).encode("utf-8"))

    for item in results[:100]:
        yield item


def main():
    workspace_path = '/home/cally/jina/news'
    os.environ['TMP_WORKSPACE'] = workspace_path
    data_fn = os.path.join(workspace_path, "news2016zh_valid.json")
    flow = (Flow().add(name='extractor', yaml_path='images/extractor/extractor.yml')
            .add(name='md_indexer', yaml_path='images/doc_indexer/doc_indexer.yml', needs='gateway')
            .add(name='encoder', yaml_path='images/encoder/encoder.yml', needs='extractor', timeout_ready=600000,
                 replicas=1)
            .add(name='cc_indexer', yaml_path='images/chunk_indexer/chunk_indexer.yml',
                 needs='encoder')
            .join(['cc_indexer', 'md_indexer']))
    with flow.build() as f:
        f.index(raw_bytes=read_data(data_fn))

if __name__ == '__main__':
    main()
