__copyright__ = "Copyright (c) 2020 Jina AI Limited. All rights reserved."
__license__ = "Apache-2.0"

import os
import zipfile
import json

root_path = '/tmp/jina/'
demo_name = 'webqa'
workspace = os.path.join(root_path, demo_name)
if not os.path.exists(workspace):
    os.mkdir(workspace)

fz = zipfile.ZipFile(os.path.join('/tmp', 'webtext2019zh.zip'), 'r')

for file in fz.namelist():
    fz.extract(file, workspace)

for filename in os.listdir(workspace):
    if not filename.endswith('.json') or filename.startswith('pre_'):
        continue

    items = {}
    with open(os.path.join(workspace, filename), 'r', encoding='utf-8') as f:
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

    items = [json.dumps(v, ensure_ascii=False) for k, v in items.items() if isinstance(v, dict)]
    with open(os.path.join(workspace, 'pre_%s' % filename), 'w', encoding='utf-8') as writer:
        writer.write('\n'.join(items))
