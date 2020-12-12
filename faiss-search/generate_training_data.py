__copyright__ = "Copyright (c) 2020 Jina AI Limited. All rights reserved."
__license__ = "Apache-2.0"

import gzip
import os
from read_vectors_files import fvecs_read

os.environ['JINA_TMP_DATA_DIR'] = '/tmp/jina/faiss/siftsmall'
train_filepath = 'workspace/index_workspace/train.tgz'
train_fvecs_path = os.path.join(os.environ['JINA_TMP_DATA_DIR'], 'siftsmall_learn.fvecs')
train_data = fvecs_read(train_fvecs_path)
with gzip.open(train_filepath, 'wb', compresslevel=1) as f:
    f.write(train_data.tobytes())
