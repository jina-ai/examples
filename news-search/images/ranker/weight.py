
from jina.drivers import BaseExecutableDriver

class ChunkWeightDriver(BaseExecutableDriver):
    def __init__(self, reverse: bool = False, *args, **kwargs):
        """ do weight into score in top results of chunks

        :param reverse: whether the score multiply the reciprocal of weight, if True, the score multiply 1/weight, else
                        score multiply weight
        """
        super().__init__(*args, **kwargs)
        self.reverse = reverse

    def __call__(self, *args, **kwargs):
        for d in self.req.docs:
            for c in d.chunks:
                for k in c.topk_results:
                    k.score.value = k.score.value * (1 / k.match_chunk.weight) * (1 / c.weight) if self.reverse else \
                        k.score.value * k.match_chunk.weight * c.weight