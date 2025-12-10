"""
Pytest configuration and fixtures
"""
import pytest
import boto3
from moto import mock_aws
import os


@pytest.fixture
def aws_credentials():
    """Mock AWS credentials for testing"""
    os.environ['AWS_ACCESS_KEY_ID'] = 'testing'
    os.environ['AWS_SECRET_ACCESS_KEY'] = 'testing'
    os.environ['AWS_SECURITY_TOKEN'] = 'testing'
    os.environ['AWS_SESSION_TOKEN'] = 'testing'
    os.environ['AWS_DEFAULT_REGION'] = 'us-east-1'


@pytest.fixture
def s3_mock(aws_credentials):
    """Mock S3 service"""
    with mock_aws():
        yield boto3.client('s3', region_name='us-east-1')


@pytest.fixture
def s3_bucket(s3_mock):
    """Create a test S3 bucket"""
    bucket_name = 'test-bucket'
    s3_mock.create_bucket(Bucket=bucket_name)
    return bucket_name


@pytest.fixture
def sample_request_data():
    """Sample valid request data"""
    return {
        'fileName': 'test-image.jpg',
        'contentType': 'image/jpeg'
    }


@pytest.fixture
def sample_lambda_event(sample_request_data):
    """Sample Lambda event"""
    import json
    return {
        'httpMethod': 'POST',
        'body': json.dumps(sample_request_data)
    }


@pytest.fixture
def allowed_content_types():
    """List of allowed content types"""
    return [
        'image/jpeg',
        'image/jpg',
        'image/png',
        'image/gif',
        'image/webp'
    ]
