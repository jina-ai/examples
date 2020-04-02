
import json
import os

from google.protobuf.json_format import MessageToDict
from jina.flow import Flow

workspace_path = '/tmp/jina/webqa/'
index_file = 'web_text_zh_valid.json'
query_file = 'web_text_zh_valid.json'
do_index = False

os.environ['TMP_WORKSPACE'] = workspace_path
os.environ['REPLICAS'] = '1'

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

def print_topk(resp, fp):
    for d in resp.search.docs:
        v = MessageToDict(d, including_default_value_fields=True)
        v['metaInfo'] = d.raw_bytes.decode()
        for k, kk in zip(v['topkResults'], d.topk_results):
            k['matchDoc']['metaInfo'] = kk.match_doc.raw_bytes.decode()
        fp.write(json.dumps(v, sort_keys=True, indent=4)+"\n")

if do_index:
    # index
    f = Flow.load_config('flow_index.yml')
    data_fn = os.path.join(workspace_path, index_file)
    with f.build() as fl:
        fl.index(raw_bytes=read_data(data_fn))

else:
    # query
    q = Flow.load_config('flow_query.yml')
    data_fn = os.path.join(workspace_path, query_file)
    with open("{}/query_result.json".format(os.environ['TMP_WORKSPACE']), "w") as fp:
        with q.build() as fl:
            pr = lambda x: print_topk(x, fp)
            fl.search(raw_bytes=read_data(data_fn), callback=pr)