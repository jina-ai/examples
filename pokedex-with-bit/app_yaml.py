__copyright__ = "Copyright (c) 2021 Jina AI Limited. All rights reserved."
__license__ = "Apache-2.0"

import json
import os
import sys

from jina import Flow, DocumentArray
from jina.logging import default_logger as logger
from executors import ImageCrafter

IMAGE_SRC = 'data/**/*.png'


def main():
    # This function runs indexing for all images and then starts the restful query API
    f = Flow.load_config('flows/index.yml')
    with f:
        f.index(inputs=DocumentArray.from_files(IMAGE_SRC),
                request_size=1, read_mode='rb', size=1)


if __name__ == '__main__':
    workspace = os.environ['JINA_WORKSPACE']
    if os.path.exists(workspace):
        logger.error(f'\n +----------------------------------------------------------------------------------+ \
                \n |                                   🤖🤖🤖                                         | \
                \n | The directory {workspace} already exists. Please remove it before indexing again.  | \
                \n |                                   🤖🤖🤖                                         | \
                \n +----------------------------------------------------------------------------------+')
        sys.exit(1)
    main()
