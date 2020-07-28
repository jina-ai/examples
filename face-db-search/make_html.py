__copyright__ = "Copyright (c) 2020 Jina AI Limited. All rights reserved."
__license__ = "Apache-2.0"

import os
import io
import webbrowser
from PIL import Image
from jina.flow import Flow
from pkg_resources import resource_filename

image_src = '/tmp/jina/celeb/lfw/**/*.jpg'
parallel = 1
shards = 8

os.environ['PARALLEL'] = str(parallel)
os.environ['SHARDS'] = str(shards)
os.environ['TMP_WORKSPACE'] = '/tmp/jina/workspace'
os.environ['TMP_RESULTS'] = '/tmp/jina/workspace/results'
os.environ['WORKDIR'] = '/tmp/jina/workspace'
os.environ['JINA_PORT'] = os.environ.get('JINA_PORT', str(45696))
os.environ['COLOR_CHANNEL_AXIS'] = str(0)

f = Flow.load_config('flow-query.yml')
f.use_grpc_gateway()

result_html = []
os.makedirs(os.environ['TMP_RESULTS'], exist_ok=True)

def print_result(resp):
    for d in resp.search.docs:
        vi = d.uri
        result_html.append(f'<tr><td><img src="{vi}"/></td><td>')
        for match in d.matches:
            im = Image.open(io.BytesIO(match.meta_info))
            fname="{}.jpg".format(match.id)
            fname = os.path.join(os.environ['TMP_RESULTS'], fname)
            im.save(fname)
            result_html.append(f'<img src="{fname}" />')
        result_html.append('</td></tr>\n')

def write_html(html_path):
    with open(resource_filename('jina', '/'.join(('resources', 'helloworld.html'))), 'r') as fp, \
            open(html_path, 'w') as fw:
        t = fp.read()
        t = t.replace('{% RESULT %}', '\n'.join(result_html))
        fw.write(t)

    url_html_path = 'file://' + os.path.abspath(html_path)

    try:
        webbrowser.open(url_html_path, new=2)
    except:
        pass


with f:
    f.search_files(image_src, sampling_rate=.01, batch_size=8, output_fn=print_result, top_k=5)

write_html('result.html')
