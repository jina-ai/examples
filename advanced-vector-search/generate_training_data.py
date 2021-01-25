__copyright__ = "Copyright (c) 2021 Jina AI Limited. All rights reserved."
__license__ = "Apache-2.0"

import gzip
import os

from read_vectors_files import fvecs_read

os.environ['JINA_DATASET_NAME'] = os.environ.get('JINA_DATASET_NAME', 'siftsmall')
os.environ['JINA_TMP_DATA_DIR'] = os.environ.get('JINA_TMP_DATA_DIR', './')
dataset_name = os.environ['JINA_DATASET_NAME']
tmp_data_dir = os.environ['JINA_TMP_DATA_DIR']
data_dir = os.path.join(tmp_data_dir, dataset_name)
train_filepath = 'workspace/train.tgz'
train_fvecs_path = os.path.join(data_dir, f'{dataset_name}_learn.fvecs')
train_data = fvecs_read(train_fvecs_path)
with gzip.open(train_filepath, 'wb', compresslevel=1) as f:
    f.write(train_data.tobytes())
