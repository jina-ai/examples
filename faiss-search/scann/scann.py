__copyright__ = "Copyright (c) 2020 Jina AI Limited. All rights reserved."
__license__ = "Apache-2.0"

from typing import Tuple

import numpy as np

from jina.executors.indexers.vector import BaseNumpyIndexer


class ScannIndexer(BaseNumpyIndexer):
    """Scann powered vector indexer

    For more information about the Scann supported parameters, please consult:
        - https://github.com/google-research/google-research/tree/master/scann

    .. note::
        Scann package dependency is only required at the query time.
    """

    def __init__(self, train_filepath: str = None, num_leaves: int = 2000, num_leaves_to_search: int = 100, training_sample_size: int = 250000,
                 scoring: str = "score_ah", anisotropic_quantization_threshold: float = 0.2, *args, **kwargs):
        """
        Initialize an ScannIndexer

        :param num_leaves: The higher num_leaves, the higher-quality the partitioning will be. It should be roughly the square root of the number of datapoints.
        :param scoring: It can be score_brute_force and score_ah (asymmetric hashing)
        :param args:
        :param kwargs:
        """
        super().__init__(*args, **kwargs)
        self.train_filepath = train_filepath
        self.num_leaves = num_leaves
        self.num_leaves_to_search = num_leaves_to_search
        self.training_sample_size = training_sample_size
        self.scoring = scoring
        self.anisotropic_quantization_threshold = anisotropic_quantization_threshold

    def build_advanced_index(self, vecs: 'np.ndarray'):
        """Load vectors into Scann indexers """
        import scann
        normalized_dataset = vecs / np.linalg.norm(vecs, axis=1)[:, np.newaxis]
        _index = scann.ScannBuilder(normalized_dataset, 10, "dot_product").tree(self.num_leaves, self.num_leaves_to_search, self.train_filepath)
        return _index

