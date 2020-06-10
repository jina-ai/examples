__copyright__ = "Copyright (c) 2020 Jina AI Limited. All rights reserved."
__license__ = "Apache-2.0"

import os
import webbrowser

from jina.flow import Flow
from pkg_resources import resource_filename

image_src = '/tmp/jina/celeb/lfw/**/*.jpg'
replicas = 1
shards = 8

os.environ['REPLICAS'] = str(replicas)
os.environ['SHARDS'] = str(shards)
os.environ['TMP_WORKSPACE'] = '/tmp/jina/workspace'
os.environ['WORKDIR'] = '/tmp/jina/workspace'
os.environ['JINA_PORT'] = os.environ.get('JINA_PORT', str(45678))
os.environ['COLOR_CHANNEL_AXIS'] = str(0)

f = Flow.load_config('flow-query.yml')
f.use_grpc_gateway()

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

def save_topk(resp, output_fn=None):
    results = []
    for d in resp.search.docs:
        cur_result = []
        d_fn = d.meta_info.decode()
        cur_result.append(d_fn)
        print("-" * 20)
        print(f'query image: {d_fn}')
        print('matched images' + "*" * 10)
        print("{}".format(d.buffer.decode()))
        for idx, kk in enumerate(d.topk_results):
            score = kk.score.value
            if score < 0.0:
                continue
            m_fn = kk.match_doc.buffer.decode()
            print('{:>2d}:({:f}):{}'.format(
                idx, score, m_fn))
            cur_result.append(m_fn)
        results.append(cur_result)
    if output_fn is not None:
        import matplotlib.pyplot as plt
        import matplotlib.image as mpimg
        top_k = max([len(r) for r in results])
        num_q = len(resp.search.docs)
        f, ax = plt.subplots(num_q, top_k, figsize=(8, 20), squeeze=False)
        for q_idx, r in enumerate(results):
            for m_idx, img in enumerate(r):
                fname = os.path.split(img)[-1]
                names=fname.split('_')[:-1]
                fname=''.join(names)
                fname = f'Query: {fname}' if m_idx == 0 else f'top_{m_idx}: {fname}'
                ax[q_idx][m_idx].imshow(mpimg.imread(img))
                ax[q_idx][m_idx].set_title(fname, fontsize=7)
        [aa.axis('off') for a in ax for aa in a]
        plt.tight_layout()
        plt.savefig(output_fn)


with f:
    ppr = lambda x: save_topk(x, os.path.join(os.environ['TMP_DATA_DIR'], 'query_results.png'))
    f.search_files(image_src, sampling_rate=.01, batch_size=8, output_fn=print_result, top_k=5)

write_html('result.html')
