import glob
import os
import random
import webbrowser

from jina.enums import ClientInputType
from jina.executors.crafters.mime import Bytes2DataURICrafter
from jina.flow import Flow
from pkg_resources import resource_filename

# replace this to whatever dir has png, it doesn't care whether its is pokemon, as long as there is a PNG it's fine
image_src = 'data/**/*.png'
replicas = 1
shards = 8
sampling_rate = .99

os.environ['REPLICAS'] = str(replicas)
os.environ['SHARDS'] = str(shards)
os.environ['WORKDIR'] = './workspace'
os.environ['JINA_PORT'] = os.environ.get('JINA_PORT', str(45678))

f = Flow.load_config('flow-query.yml')
f.use_grpc_gateway()  # use gRPC gateway for better batch efficiency


def input_fn():
    b2d = Bytes2DataURICrafter('png')
    for g in glob.glob(image_src, recursive=True):
        if random.random() > sampling_rate:
            with open(g, 'rb') as fp:
                yield b2d.make_datauri(b2d.mimetype, fp.read())


result_html = []


def print_result(resp):
    for d in resp.search.docs:
        vi = d.data_uri
        result_html.append(f'<tr><td><img src="{vi}"/></td><td>')
        for kk in d.topk_results:
            kmi = kk.match_doc.data_uri
            result_html.append(f'<img src="{kmi}" style="opacity:{kk.score.value}"/>')
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
    f.search(input_fn, batch_size=8, output_fn=print_result,
             top_k=20, input_type=ClientInputType.DATA_URI)

write_html('result.html')
