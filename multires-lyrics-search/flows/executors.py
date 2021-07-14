""" Executors required for the multires example """

from itertools import groupby
from jina import Executor, DocumentArray, requests


class MinRanker(Executor):
    def __init__(
            self,
            *args,
            **kwargs,
    ):
        super().__init__(*args, **kwargs)

    @requests(on='/search')
    def min_rank(self, docs: DocumentArray, **kwargs):
        for doc in docs:
            matches_of_chunks = []
            for chunk in doc.chunks:
                for match in chunk.matches:
                    matches_of_chunks.append(match)

            groups = groupby(sorted(matches_of_chunks, key=lambda d: d.parent_id), lambda d: d.parent_id)
            for key, group in groups:
                chunk_match_list = list(group)
                chunk_match_list.sort(key=lambda m: -m.scores['cosine'].value)
                match = chunk_match_list[0]
                match.id = key
                doc.matches.append(match)
            doc.matches.sort(key=lambda d: -d.scores['cosine'].value)