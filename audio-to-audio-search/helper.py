import glob
import logging
import os
from pathlib import Path
import re
import random
import shutil
import subprocess

from prettytable import PrettyTable
from jina import Document, DocumentArray
import webbrowser


result_html = []
accuracy = None
ID_LEN = 11
TOP_K = 5


def get_logger():
    logger = logging.getLogger('app')
    logger.setLevel(logging.INFO)
    formatter = logging.Formatter('%(message)s')
    sh = logging.StreamHandler()
    sh.setFormatter(formatter)
    sh.setLevel(logging.INFO)
    logger.addHandler(sh)
    return logger


logger = get_logger()


def create_docs(filefolder_path, num_docs):
    docs = []
    import librosa as lr
    logger.info('Creating docs..')
    for file_path in sorted(glob.glob(filefolder_path))[:num_docs]:
        id = os.path.basename(file_path).split('.')[0]
        blob, sample_rate = lr.load(file_path)
        docs.append(Document(id=id, blob=blob, tags={'file': file_path, 'sample_rate': sample_rate}))
    logger.info('docs created')
    return DocumentArray(docs)


def create_query_audios(num_docs):
    mp3_folder = Path(__file__).parent / 'data' / 'mp3'
    input_docs_folder = mp3_folder / 'index'
    output_docs_folder = mp3_folder / 'query'
    mp3_folder.mkdir(exist_ok=True)
    if output_docs_folder.is_dir():
        shutil.rmtree(output_docs_folder)
    output_docs_folder.mkdir()
    input_docs_filenames = glob.glob(str(input_docs_folder / '*.mp3'))

    if len(input_docs_filenames) == 0: 
        raise FileNotFoundError('index audios not found, cannot create query docs')

    for input_file in random.sample(input_docs_filenames, k=num_docs):
        id = re.match(r'index_(.*).mp3', os.path.basename(input_file))[1][-ID_LEN:]
        output_file = f"query_{id}.mp3"
        startTime = random.random() * 5
        endTime = startTime + random.random() * 4 + 3
        cmd = ['ffmpeg', '-i', input_file, '-ss', str(startTime), '-to', str(endTime), '-async', '1', output_file]
        subprocess.call(cmd, cwd=str(output_docs_folder))


def report_results(response, threshold):
    """
    Callback function to receive results.

    :param resp: returned response with data
    """
    global accuracy
    pred_list = []
    table = PrettyTable()
    table.field_names = ['target', 'prediction', 'is_correct']
    for i, doc in enumerate(response.docs):
        if not doc.matches:
            continue
        match = doc.matches[0]
        target_result = os.path.basename(doc.tags["file"]).split('.')[0][-ID_LEN:]
        pred_result = os.path.basename(match.tags["file"]).split('.')[0][-ID_LEN:]
        pred_result = pred_result if threshold is None or 1 - match.scores['cosine'].value > threshold else 'None'
        table.add_row([target_result, pred_result, target_result == pred_result])
        pred_list.append(target_result == pred_result)

        query_html = f"""
            <audio id="query{i}" src="{'file://' + doc.tags['file']}" preload="none" type="audio/mp3"></audio>
            <button style="padding: 1em" onclick=" if (prev!=null){{prev.pause(); prev.currentTIme=0;}} prev=document.getElementById('query{i}'); prev.play();">
                <i class='fa fa-volume-up fa-2x'></i></a>
            </button>
        """
        seen = set()
        result_html.append(f'<tr><td>{query_html}</td><td>')
        print('wt, ', len(doc.matches))
        for j, match in enumerate(doc.matches):
            if len(seen) >= TOP_K: break
            if match.tags['file'] in seen: continue
            seen.add(match.tags['file'])
            match_html = f"""
                <audio id="query{i}_match{j}" src="{'file://' + match.tags['file']}" preload="none" type="audio/mp3"></audio>
                <button style="padding: 1em" onclick="if(prev!=null){{prev.pause(); prev.currentTIme=0;}} prev=document.getElementById('query{i}_match{j}'); prev.play();">
                    <i class='fa fa-volume-up fa-2x'></i>
                </button>
            """
            result_html.append(match_html)
        result_html.append('</td></tr>\n')

    logger.info(table)
    accuracy = sum(pred_list) / len(pred_list)
    logger.info(f'accuracy: {accuracy}')




def write_html(html_path):
    """
    Method to present results in browser.

    :param html_path: path of the written html
    """
    global accuracy
    with open(
        os.path.join(os.path.dirname(os.path.realpath(__file__)), 'demo.html')
    ) as fp, open(html_path, 'w') as fw:
        t = fp.read()
        t = t.replace('{% RESULT %}', '\n'.join(result_html))
        t = t.replace(
            '{% PRECISION_EVALUATION %}',
            '{:.2f}%'.format(accuracy * 100.0),
        )
        t = t.replace('{% TOP_K %}', str(TOP_K))
        fw.write(t)

    url_html_path = 'file://' + os.path.abspath(html_path)

    try:
        webbrowser.open(url_html_path, new=2)
    except:
        pass  # intentional pass, browser support isn't cross-platform
    finally:
        logger.info(
            f'You should see a "demo.html" opened in your browser, '
            f'if not you may open {url_html_path} manually'
        )


