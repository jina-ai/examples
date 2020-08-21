__copyright__ = "Copyright (c) 2020 Jina AI Limited. All rights reserved."
__license__ = "Apache-2.0"

import os
import io
import webbrowser
from PIL import Image
from jina.flow import Flow
from pkg_resources import resource_filename


result_html = []

def config():
    os.environ['PARALLEL'] = str(1)
    os.environ['SHARDS'] = str(8)
    os.environ['COLOR_CHANNEL_AXIS'] = str(0)
    os.environ['TMP_WORKSPACE'] = '/tmp/jina/workspace'
    os.environ['TMP_RESULTS'] = '/tmp/jina/workspace/results'
    os.makedirs(os.environ['TMP_RESULTS'], exist_ok=True)
    os.environ['JINA_PORT'] = os.environ.get('JINA_PORT', str(45696))


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


def main():
    config()
    image_src = '/tmp/jina/celeb/lfw/**/*.jpg'
    f = Flow.load_config('flow-query.yml')
    f.use_grpc_gateway()

    with f:
        f.search_files(image_src, sampling_rate=.01, batch_size=8, output_fn=print_result, top_k=5)

    write_html('result.html')


if __name__ == '__main__':
    main()
    