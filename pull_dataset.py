# This script is only used by the CI Pipeline
import logging
import os

import click
from jinacld_tools.aws.services.s3 import S3


BUCKET_NAME = "kaggle-data-set-bucket"
log = logging.getLogger(__name__)


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
    assert os.path.isdir(pull_to_dir), "The pull dir parameter must be a directory"
    save_path = os.path.join(pull_to_dir, data_set)
    s3 = S3(BUCKET_NAME)
    try:
        s3.get(data_set, save_path)
    except Exception as e:
        log.error(e)


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    main()
