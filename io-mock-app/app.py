__copyright__ = "Copyright (c) 2020 Jina AI Limited. All rights reserved."
__license__ = "Apache-2.0"

import os
import random
import sys

from jina.drivers import BaseDriver
from jina.flow import Flow

class RandomPopRanker(BaseDriver):
    max_num_docs = 100

    def __call__(self, *args, **kwargs):
        for d in self.req.docs:
            for k in range(self.req.top_k):
                r = d.topk_results.add()
                r.match_doc.doc_id = random.randint(0, self.max_num_docs)
                r.score.value = random.random()


def config():
    os.environ['WORKDIR'] = './workspace'
    os.makedirs(os.environ['WORKDIR'], exist_ok=True)
    os.environ['JINA_PORT'] = os.environ.get('JINA_PORT', str(45678))


def index():
    f = Flow().add(uses='indexer.yml')
    with f:
        f.index_files(sys.argv[2])


def search():
    f = (Flow(rest_api=True, port_expose=int(os.environ['JINA_PORT']))
         .add(uses='- !RandomPopRanker {}')
         .add(uses='indexer.yml'))
    with f:
        f.block()


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print('choose between "index" and "search" mode')
        exit(1)
    if sys.argv[1] == 'index':
        config()
        workspace = os.environ['WORKDIR']
        if os.path.exists(workspace):
            print(f'\n +---------------------------------------------------------------------------------+ \
                    \n |                                   🤖🤖🤖                                        | \
                    \n | The directory {workspace} already exists. Please remove it before indexing again. | \
                    \n |                                   🤖🤖🤖                                        | \
                    \n +---------------------------------------------------------------------------------+')
        index()
    elif sys.argv[1] == 'search':
        config()
        search()
    else:
        raise NotImplementedError(f'unsupported mode {sys.argv[1]}')
