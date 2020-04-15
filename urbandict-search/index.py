import os
import csv
import json
from collections import defaultdict
from jina.flow import Flow


def read_data(fn, max_sample_size=1000):
    illegal_counts = 0
    with open(fn, "r") as f:
        r = csv.reader(f)
        word2def = defaultdict(list)
        for idx, l in enumerate(r):
            if idx == 0:
                continue
            if len(l) != 6:
                illegal_counts += 1
                continue
            _, word, up_votes, down_votes, _, word_def = l
            up_votes = int(up_votes)
            down_votes = int(down_votes)
            weight = up_votes * 1.0 / down_votes if down_votes != 0 else up_votes
            if len(word_def) == 0:
                continue
            word2def[word].append({"text": word_def, "weight": weight})
    print("illegal counts: {}/{}".format(illegal_counts, idx))
    print("word2def size: {}/{}".format(len(word2def), idx))
    count = 0
    result = []
    for k, v in word2def.items():
        json_dict = {"word": k, "def": v}
        if len(v) == 0:
            continue
        count += 1
        if count >= max_sample_size:
            break
        result.append(("{}".format(json.dumps(json_dict, ensure_ascii=False))).encode("utf8"))
    for r in result:
        yield r


def main():
    workspace_path = '/tmp/jina/urbandict'
    os.environ['TMP_WORKSPACE'] = workspace_path
    data_fn = os.path.join(workspace_path, "urbandict-word-defs.csv")

    flow = (Flow().add(
        name='extractor', yaml_path='yaml/extractor.yml'
    ).add(
        name='meta_doc_indexer', yaml_path='yaml/meta_doc_indexer.yml'
    ).add(
        name='encoder', yaml_path='yaml/encoder.yml',
        needs='extractor', timeout_ready=600000
    ).add(
        name='compound_chunk_indexer', yaml_path='yaml/compound_chunk_indexer.yml', batch_size=10,
        needs='encoder'
    ).add(
        name='merger', yaml_path='yaml/merger.yml',
        needs=['meta_doc_indexer', 'compound_chunk_indexer']
    ))

    with flow.build() as f:
        f.index(raw_bytes=read_data(data_fn, max_sample_size=50), prefetch=2)


if __name__ == '__main__':
    main()
