import os
import zipfile

data_fn = "urbandict-word-defs.csv"
workspace_path = '/tmp/jina/urbandict'
if os.path.exists(workspace_path):
    print("data output dir: {}".format(workspace_path))
    os.mkdir(workspace_path)

tmp_data_path = os.path.join(workspace_path, data_fn)

with zipfile.ZipFile('/tmp/urban-dictionary-words-dataset.zip') as z:
    with open(tmp_data_path, 'wb') as f:
        f.write(z.read(data_fn))
