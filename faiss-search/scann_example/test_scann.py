import h5py
import requests

import os
import unittest
import gzip

import numpy as np
from jina.executors.indexers import BaseIndexer
from .scann_example import ScannIndexer

# fix the seed here
np.random.seed(500)
retr_idx = None
vec_idx = np.random.randint(0, high=100, size=[10])
vec = np.array(np.random.random([10, 10]), dtype=np.float32)
query = np.array(np.random.random([10, 10]), dtype=np.float32)
cur_dir = os.path.dirname(os.path.abspath(__file__))


class ScannTestCase(unittest.TestCase):

    def test_scann_indexer(self):

        with ScannIndexer(index_filename='scann.test_small_num_neighbors.gz') as a:
            a.add(vec_idx, vec)
            a.save()
            self.assertTrue(os.path.exists(a.index_abspath))
            index_abspath = a.index_abspath
            save_abspath = a.save_abspath

        with BaseIndexer.load(save_abspath) as b:
            idx, dist = b.query(query, top_k=4)
            print(idx, dist)
            global retr_idx
            if retr_idx is None:
                retr_idx = idx
            else:
                np.testing.assert_almost_equal(retr_idx, idx)
            self.assertEqual(idx.shape, dist.shape)
            self.assertEqual(idx.shape, (10, 4))

        #self.add_tmpfile(index_abspath, save_abspath)


if __name__ == '__main__':
    unittest.main()
