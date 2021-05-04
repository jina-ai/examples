# This script is only used by the CI Pipeline
import logging
import os

import click
from jinacld_tools.aws.services.s3 import S3


BUCKET_NAME = "jina-examples-datasets"
log = logging.getLogger(__name__)


def _check_credentials_exist():
    assert os.environ.get('AWS_ACCESS_KEY_ID') is not None, 'Missing access key'
    assert len(os.environ['AWS_ACCESS_KEY_ID']) > 0, 'Empty access key'
    assert os.environ.get('AWS_SECRET_ACCESS_KEY') is not None, 'Missing secret key'
    assert len(os.environ['AWS_SECRET_ACCESS_KEY']) > 0, 'Empty secret key'


@click.command()
@click.option(
    "--data-set",
    "-d",
    type=str,
    required=True
)
@click.option(
    "--pull-to-dir",
    "-p",
    type=click.Path(exists=False),
    required=True
)
def main(data_set: str, pull_to_dir: str):
    _check_credentials_exist()
    assert os.path.isdir(pull_to_dir), "The pull dir parameter must be an existing directory"
    save_path = os.path.join(pull_to_dir, data_set)
    s3 = S3(BUCKET_NAME)
    try:
        s3.get(data_set, save_path)
    except Exception as e:
        log.error(e)


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    main()
