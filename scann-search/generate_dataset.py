__copyright__ = "Copyright (c) 2020 Jina AI Limited. All rights reserved."
__license__ = "Apache-2.0"

import os
import numpy as np
import h5py

os.environ['TMP_DATA_DIR'] = '/tmp/jina/scann'
loc = os.path.join(os.environ['TMP_DATA_DIR'], 'glove_angular.hdf5')
print(loc)

with h5py.File(loc, "r") as f:
    # List all groups
    print("Keys: %s" % f.keys())
    a_group_key = list(f.keys())[0]

    # Get the data
    data = list(f[a_group_key])

glove_h5py = h5py.File(loc)


dataset = glove_h5py['train']
queries = glove_h5py['test']
print(dataset.shape)
print(queries.shape)
