# This script is only used by the CI Pipeline
import logging
import os

import click
from jinacld_tools.aws.services.s3 import S3Bucket


BUCKET_NAME = "jina-examples-datasets"
log = logging.getLogger(__name__)


def _check_credentials_exist():
    assert os.environ.get('AWS_ACCESS_KEY_ID') is not None,\
        'AWS_ACCESS_KEY_ID is not present in the environment variables but required for this script.'
    assert len(os.environ['AWS_ACCESS_KEY_ID']) > 0, \
        'AWS_ACCESS_KEY_ID was set in the environment but has length zero.'
    assert os.environ.get('AWS_SECRET_ACCESS_KEY') is not None,\
        'AWS_SECRET_ACCESS_KEY is not present in the environment variables but required for this script.'
    assert len(os.environ['AWS_SECRET_ACCESS_KEY']) > 0,\
        'AWS_SECRET_ACCESS_KEY was set in the environment but has length zero.'


@click.command()
@click.option(
    "--data-set",
    "-d",
    type=str,
    required=True,
    help='Path to the data-set in the S3 bucket relative to the root.'
)
@click.option(
    "--pull-to-dir",
    "-p",
    type=click.Path(exists=False),
    required=True,
    help='Directory to download the data to. Must exist beforehand.'
)
def main(data_set: str, pull_to_dir: str):
    _check_credentials_exist()
    assert os.path.isdir(pull_to_dir), "The pull dir parameter must be an existing directory"
    save_path = os.path.join(pull_to_dir, data_set)
    s3 = S3Bucket(BUCKET_NAME)
    try:
        s3.get(data_set, save_path)
    except Exception as e:
        log.error(e)


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    main()
