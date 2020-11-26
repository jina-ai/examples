__copyright__ = "Copyright (c) 2020 Jina AI Limited. All rights reserved."
__license__ = "Apache-2.0"

import os
import webbrowser

from jina.flow import Flow
from pkg_resources import resource_filename

# replace this to whatever dir has png, it doesn't care whether its is pokemon, as long as there is a PNG it's fine
image_src = 'data/**/*.png'
parallel = 1
shards = 8

os.environ['JINA_PARALLEL'] = str(parallel)
os.environ['JINA_SHARDS'] = str(shards)
os.environ['JINA_WORKSPACE'] = './workspace'
os.environ['JINA_PORT'] = os.environ.get('JINA_PORT', str(45678))

f = Flow.load_config('flows/query.yml')
f.use_grpc_gateway()  # use gRPC gateway for better batch efficiency

result_html = []


def print_result(resp):
    for d in resp.search.docs:
        vi = d.data_uri
        result_html.append(f'<tr><td><img src="{vi}"/></td><td>')
        for match in d.matches:
            uri = match.data_uri
            result_html.append(f'<img src="{uri}" style="opacity:{match.score.value}"/>')
            # k['score']['explained'] = json.loads(kk.score.explained)
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
    f.search_files(image_src, sampling_rate=.01, batch_size=8, output_fn=print_result, top_k=20)

write_html('result.html')
