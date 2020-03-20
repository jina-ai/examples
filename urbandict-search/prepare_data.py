import os
import zipfile

data_fn = "urbandict-word-defs.csv"
root_path = '/tmp/jina/'
demo_name = 'urbandict'
workspace_path = os.path.join(root_path, demo_name)
if not os.path.exists(workspace_path):
    print("data output dir: {}".format(workspace_path))
    os.mkdir(root_path)
    os.mkdir(workspace_path)

tmp_data_path = os.path.join(workspace_path, data_fn)

with zipfile.ZipFile('/tmp/urban-dictionary-words-dataset.zip') as z:
    with open(tmp_data_path, 'wb') as f:
        f.write(z.read(data_fn))
