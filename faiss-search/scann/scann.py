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

    def __init__(self, train_filepath: str = None,
                 num_leaves: int = 2000,
                 num_leaves_to_search: int = 100,
                 training_iterations: int = 10,
                 distance_measure: str = "dot_product",
                 training_sample_size: int = 250000,
                 scoring: str = "score_ah",
                 anisotropic_quantization_threshold: float = 0.2,
                 dimensions_per_block: int = 2,
                 *args, **kwargs):
        """
        Initialize an ScannIndexer

        :param num_leaves: The higher num_leaves, the higher-quality the partitioning will be. It should be roughly the square root of the number of datapoints.
        :param scoring: It can be score_brute_force and score_ah (asymmetric hashing)
        :param training_iterations: Default is 10
        :param distance_measure: It can be dot_product or squared_l2
        :param training_sample_size: Default is 25k
        :param scoring: It can be score_ah or score_bf for brute force
        :param anisotropic_quantization_threshold:
        :param dimensions_per_block: Recommended for AH is 2
        :param args:
        :param kwargs:
        """
        super().__init__(*args, **kwargs)
        self.train_filepath = train_filepath
        self.num_leaves = num_leaves
        self.training_iterations = training_iterations
        self.distance_measure = distance_measure
        self.num_leaves_to_search = num_leaves_to_search
        self.training_sample_size = training_sample_size
        self.scoring = scoring
        self.anisotropic_quantization_threshold = anisotropic_quantization_threshold
        self.dimensions_per_block = dimensions_per_block

    def build_advanced_index(self, vecs: 'np.ndarray'):
        """Load vectors into Scann indexers """
        import scann
        _index = scann.ScannBuilder(vecs, self.training_iterations, self.distance_measure).\
            tree(self.num_leaves, self.num_leaves_to_search, self.training_sample_size).\
            score_ah(self.dimensions_per_block, self.anisotropic_quantization_threshold).reorder(100).create_pybind()
        return _index

