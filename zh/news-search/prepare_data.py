__copyright__ = "Copyright (c) 2020 Jina AI Limited. All rights reserved."
__license__ = "Apache-2.0"

import json
import os
import zipfile
import sys

root_path = '/tmp/jina/'
demo_name = 'news'
workspace = os.path.join(root_path, demo_name)
if not os.path.exists(workspace):
    os.makedirs(workspace)

fz = zipfile.ZipFile(os.path.join('/tmp', 'new2016zh.zip'), 'r')

for file in fz.namelist():
    if len(sys.argv)>1 and sys.argv[1] == 'valid' and not file.endswith('valid.json'):
        continue
    fz.extract(file, workspace)

for filename in os.listdir(workspace):
    if not filename.endswith('.json') or filename.startswith('pre_'):
        continue
    if len(sys.argv)>1 and sys.argv[1] == 'valid' and not filename.endswith('valid.json'):
        continue
    items = []
    with open(os.path.join(workspace, filename), 'r', encoding='utf-8') as f:
        for line in f:
            line = line.replace('\n', '')
            item = json.loads(line)
            content = item['content']
            if content == '' or len(content) < 5:
                continue

            items.append(json.dumps({'content': content}, ensure_ascii=False))

    with open(os.path.join(workspace, 'pre_%s' % filename), 'w', encoding='utf-8') as writer:
        writer.write('\n'.join(items))
