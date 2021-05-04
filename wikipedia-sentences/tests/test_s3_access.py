import os

from jinacld_tools.aws.services.s3 import S3Bucket


def test_s3_access():
    assert not os.path.isfile(path='./dummy_test_file')
    assert "AWS_ACCESS_KEY_ID" in os.environ
    assert "AWS_SECRET_ACCESS_KEY" in os.environ
    assert len(os.environ["AWS_SECRET_ACCESS_KEY"]) > 0

    S3Bucket(bucket_name='jina-examples-datasets').get(key='dummy_test_file', local_path='./dummy_test_file')
    assert os.path.isfile(path='./dummy_test_file')
