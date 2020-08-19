__copyright__ = "Copyright (c) 2020 Jina AI Limited. All rights reserved."
__license__ = "Apache-2.0"

from typing import Tuple

import numpy as np
import scann

from jina.executors.indexers.vector import BaseNumpyIndexer


class ScannIndexer(BaseNumpyIndexer):

    """Scann powered vector indexer

    For more information about the Scann supported parameters, please consult:
        - https://github.com/google-research/google-research/tree/master/scann

    .. note::
        Scann package dependency is only required at the query time.
    """

    def __init__(self,
                 num_leaves: int = 2000,
                 num_leaves_to_search: int = 100,
                 training_iterations: int = 10,
                 distance_measure: str = "dot_product",
                 training_sample_size: int = 250000,
                 scoring: str = "score_ah",
                 anisotropic_quantization_threshold: float = 0.2,
                 dimensions_per_block: int = 2,
                 reordering_num_neighbors: int = 100,
                 *args, **kwargs):
        """
        Initialize an ScannIndexer

        :param num_leaves: It should be roughly the square root of the number of datapoints.
            The higher num_leaves, the higher-quality the partitioning will be.
        :param training_iterations: Number of iterations per training. Default is 10
        :param distance_measure: The distance measurement used between the query and the points.
            It can be dot_product or squared_l2
        :param num_leaves_to_search: The amount of leaves to search.
            This should be tuned based on recall target
        :param training_sample_size: The size of the training sample.
        :param scoring: It can be score_ah (asymmetric hashing) or score_bf (brute force).
            For small datasets (less than 20k) brute force is recommended
        :param anisotropic_quantization_threshold: See https://arxiv.org/abs/1908.10396 for
            a description of this value
        :param dimensions_per_block: Recommended for AH is 2
        :param reordering_num_neighbors: Should be higher than the final number of neighbors
            If this number is increased, the accuracy will increase but it will impact speed
        """
        super().__init__(*args, **kwargs)
        self.num_leaves = num_leaves
        self.training_iterations = training_iterations
        self.distance_measure = distance_measure
        self.num_leaves_to_search = num_leaves_to_search
        self.training_sample_size = training_sample_size
        self.scoring = scoring
        self.anisotropic_quantization_threshold = anisotropic_quantization_threshold
        self.dimensions_per_block = dimensions_per_block
        self.reordering_num_neighbors = reordering_num_neighbors

    def build_advanced_index(self, vecs: 'np.ndarray'):
        """Load vectors into Scann indexers
        This is a lazy evaluation.
        The .score_ah(...) and .reorder(...) are creating configuration
        and only .create_pybind() is building the object

        1) (Optional) The first step is the partitioning, this will be done
        with .tree(...) during training time,
        and at query time it will select the top partitions
        2) The second stage is the Scoring.
            If partitioning isn't enabled it will measure the distance
            between the query and all datapoints.
            If partitioning is enabled it will measure only within the
            partition to search
        3) (Optional) This is highly recommended if AH was used.
        It will take the top k-distances and re-compute the distance.
        Then the top-k from this new measurement will be selected.
        """
        index = scann.ScannBuilder(vecs, self.training_iterations, self.distance_measure).\
            score_ah(self.dimensions_per_block, self.anisotropic_quantization_threshold).\
            reorder(self.reordering_num_neighbors).create_pybind()
        return index

    def query(self, keys: 'np.ndarray', top_k: int, *args, **kwargs) -> Tuple['np.ndarray', 'np.ndarray']:
        if self.reordering_num_neighbors < top_k:
            self.logger.warning('The number of reordering_num_neighbors should be the same or higher than top_k')

        neighbors, dist = self.query_handler.search_batched(keys, top_k)
        return neighbors, dist

