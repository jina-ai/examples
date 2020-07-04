import gzip
import os
from fvecs_read import fvecs_read

os.environ['TMP_DATA_DIR'] = '/tmp/jina/faiss/siftsmall'
train_filepath = 'workspace/train.tgz'
train_fvecs_path = os.path.join(os.environ['TMP_DATA_DIR'], 'siftsmall_learn.fvecs')
train_data = fvecs_read(train_fvecs_path)
with gzip.open(train_filepath, 'wb', compresslevel=1) as f:
    f.write(train_data.tobytes())
