__copyright__ = "Copyright (c) 2020 Jina AI Limited. All rights reserved."
__license__ = "Apache-2.0"


from jina.drivers.helper import pb2array
from jina.flow import Flow
from jina.helper import colored


def input_fn():
    with open('README.md') as fp:
        for v in fp:
            yield v


def print_embed(req):
    for d in req.docs:
        for c in d.chunks:
            embed = pb2array(c.embedding)
            text = colored(f'{c.text[:10]}...' if len(c.text) > 10 else c.text, 'blue')
            print(f'{text} embed to {embed.shape} [{embed[0]:.3f}, {embed[1]:.3f}...]')


f = (Flow(callback_on_body=True)
     .add(name='spit', uses='Sentencizer')
     .add(name='encode', uses='jinaai/hub.executors.encoders.nlp.transformers-pytorch',
          parallel=2, timeout_ready=20000))

with f:
    f.index(input_fn, batch_size=32, callback=print_embed)


