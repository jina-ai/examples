import gzip
import numpy as np
train_filepath = 'workspace/train.tgz'
train_data = np.random.rand(10000, 128)
with gzip.open(train_filepath, 'wb', compresslevel=1) as f:
    f.write(train_data.astype('float32'))
