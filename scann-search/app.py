__copyright__ = "Copyright (c) 2020 Jina AI Limited. All rights reserved."
__license__ = "Apache-2.0"


import click
import os
import string
import random
import numpy as np
import scann

from jina.flow import Flow

os.environ['TMP_DATA_DIR'] = '/tmp/jina/scann'

@click.command()
def main(task):
    if task == 'index':
        data_path = os.path.join(os.environ['TMP_DATA_DIR'], 'glove_angular.hdf5')
        flow = Flow().load_config('flow-index.yml')
    elif task == 'query':
        data_path = os.path.join(os.environ['TMP_DATA_DIR'], 'glove_angular.hdf5')
        flow = Flow().load_config('flow-query.yml')
    else:
        raise NotImplementedError(
            f'unknown task: {task}. A valid task is either `index` or `query`.')

