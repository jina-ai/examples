import h5py
import requests

import os
import unittest
import gzip

import numpy as np
from jina.executors.indexers import BaseIndexer
from scann import ScannIndexer

# fix the seed here
np.random.seed(500)
retr_idx = None
vec_idx = np.random.randint(0, high=100, size=[10])
vec = np.array(np.random.random([10, 10]), dtype=np.float32)
query = np.array(np.random.random([10, 10]), dtype=np.float32)
cur_dir = os.path.dirname(os.path.abspath(__file__))


class ScannTestCase(unittest.TestCase):

    def test_scann_indexer(self):

        loc = os.path.join(cur_dir, "glove.hdf5")

        glove_h5py = h5py.File(loc)
        list(glove_h5py.keys())
        dataset = glove_h5py['train']
        queries = glove_h5py['test']

        with ScannIndexer(
                num_leaves=2000,
                num_leaves_to_search=100,
                training_iterations=10,
                distance_measure="dot_product",
                training_sample_size=250000,
                scoring="score_ah",
                anisotropic_quantization_threshold=0.2,
                dimensions_per_block=2,
                reordering_num_neighbors=100) as a:
            a.add(vec_idx, vec)

            a.save()
            self.assertTrue(os.path.exists(a.index_abspath))
            index_abspath = a.index_abspath
            save_abspath = a.save_abspath

        with BaseIndexer.load(save_abspath) as b:
            #print("*********** dataset: ", dataset, " ***")
            searcher = ScannIndexer.build_advanced_index(self,  dataset)

            idx, dist = b.query(queries, 10)

            global retr_idx
            if retr_idx is None:
                retr_idx = idx
            else:
                np.testing.assert_almost_equal(retr_idx, idx)
            self.assertEqual(idx.shape, dist.shape)


if __name__ == '__main__':
    unittest.main()
