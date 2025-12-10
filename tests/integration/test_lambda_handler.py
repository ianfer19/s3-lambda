"""
Integration tests for Lambda handler
"""
import pytest
import json
import os
from unittest.mock import patch
from moto import mock_aws
import boto3


# Set environment variables before importing lambda_function
os.environ['S3_BUCKET_NAME'] = 'test-bucket'
os.environ['PRESIGNED_URL_EXPIRATION'] = '300'


class TestLambdaHandler:
    """Integration tests for lambda_handler"""
    
    @pytest.fixture
    def lambda_context(self):
        """Mock Lambda context"""
        class Context:
            function_name = 'test-function'
            memory_limit_in_mb = 128
            invoked_function_arn = 'arn:aws:lambda:us-east-1:123456789012:function:test-function'
            aws_request_id = 'test-request-id'
        
        return Context()
    
    @mock_aws
    def test_lambda_handler_success(self, sample_lambda_event, lambda_context, aws_credentials):
        """Test successful Lambda invocation"""
        # Setup S3 bucket
        s3_client = boto3.client('s3', region_name='us-east-1')
        s3_client.create_bucket(Bucket='test-bucket')
        
        # Import after mocking
        from lambda_function import lambda_handler
        
        # Execute
        response = lambda_handler(sample_lambda_event, lambda_context)
        
        # Assert
        assert response['statusCode'] == 200
        assert 'Access-Control-Allow-Origin' in response['headers']
        
        body = json.loads(response['body'])
        assert 'uploadUrl' in body
        assert 'fileUrl' in body
        assert 'key' in body
        assert body['key'].startswith('projects/')
    
    @mock_aws
    def test_lambda_handler_cors_preflight(self, lambda_context, aws_credentials):
        """Test CORS preflight request"""
        # Setup
        s3_client = boto3.client('s3', region_name='us-east-1')
        s3_client.create_bucket(Bucket='test-bucket')
        
        event = {'httpMethod': 'OPTIONS'}
        
        from lambda_function import lambda_handler
        
        # Execute
        response = lambda_handler(event, lambda_context)
        
        # Assert
        assert response['statusCode'] == 200
        assert 'Access-Control-Allow-Origin' in response['headers']
        assert 'Access-Control-Allow-Methods' in response['headers']
        
        body = json.loads(response['body'])
        assert body['message'] == 'OK'
    
    @mock_aws
    def test_lambda_handler_missing_filename(self, lambda_context, aws_credentials):
        """Test Lambda with missing fileName"""
        # Setup
        s3_client = boto3.client('s3', region_name='us-east-1')
        s3_client.create_bucket(Bucket='test-bucket')
        
        event = {
            'httpMethod': 'POST',
            'body': json.dumps({'contentType': 'image/jpeg'})
        }
        
        from lambda_function import lambda_handler
        
        # Execute
        response = lambda_handler(event, lambda_context)
        
        # Assert
        assert response['statusCode'] == 400
        body = json.loads(response['body'])
        assert 'error' in body
        assert 'fileName' in body['error'].lower() or body.get('field') == 'fileName'
    
    @mock_aws
    def test_lambda_handler_missing_content_type(self, lambda_context, aws_credentials):
        """Test Lambda with missing contentType"""
        # Setup
        s3_client = boto3.client('s3', region_name='us-east-1')
        s3_client.create_bucket(Bucket='test-bucket')
        
        event = {
            'httpMethod': 'POST',
            'body': json.dumps({'fileName': 'test.jpg'})
        }
        
        from lambda_function import lambda_handler
        
        # Execute
        response = lambda_handler(event, lambda_context)
        
        # Assert
        assert response['statusCode'] == 400
        body = json.loads(response['body'])
        assert 'error' in body
    
    @mock_aws
    def test_lambda_handler_invalid_content_type(self, lambda_context, aws_credentials):
        """Test Lambda with invalid content type"""
        # Setup
        s3_client = boto3.client('s3', region_name='us-east-1')
        s3_client.create_bucket(Bucket='test-bucket')
        
        event = {
            'httpMethod': 'POST',
            'body': json.dumps({
                'fileName': 'test.pdf',
                'contentType': 'application/pdf'
            })
        }
        
        from lambda_function import lambda_handler
        
        # Execute
        response = lambda_handler(event, lambda_context)
        
        # Assert
        assert response['statusCode'] == 400
        body = json.loads(response['body'])
        assert 'error' in body
        assert 'content type' in body['error'].lower()
    
    @mock_aws
    def test_lambda_handler_invalid_json(self, lambda_context, aws_credentials):
        """Test Lambda with invalid JSON"""
        # Setup
        s3_client = boto3.client('s3', region_name='us-east-1')
        s3_client.create_bucket(Bucket='test-bucket')
        
        event = {
            'httpMethod': 'POST',
            'body': 'invalid json {'
        }
        
        from lambda_function import lambda_handler
        
        # Execute
        response = lambda_handler(event, lambda_context)
        
        # Assert
        assert response['statusCode'] == 400
        body = json.loads(response['body'])
        assert 'error' in body
        assert 'json' in body['error'].lower()
    
    @mock_aws
    def test_lambda_handler_empty_body(self, lambda_context, aws_credentials):
        """Test Lambda with empty body"""
        # Setup
        s3_client = boto3.client('s3', region_name='us-east-1')
        s3_client.create_bucket(Bucket='test-bucket')
        
        event = {
            'httpMethod': 'POST',
            'body': '{}'
        }
        
        from lambda_function import lambda_handler
        
        # Execute
        response = lambda_handler(event, lambda_context)
        
        # Assert
        assert response['statusCode'] == 400
        body = json.loads(response['body'])
        assert 'error' in body
    
    @mock_aws
    def test_lambda_handler_sanitizes_filename(self, lambda_context, aws_credentials):
        """Test that Lambda sanitizes filenames"""
        # Setup
        s3_client = boto3.client('s3', region_name='us-east-1')
        s3_client.create_bucket(Bucket='test-bucket')
        
        event = {
            'httpMethod': 'POST',
            'body': json.dumps({
                'fileName': '../../etc/passwd.jpg',
                'contentType': 'image/jpeg'
            })
        }
        
        from lambda_function import lambda_handler
        
        # Execute
        response = lambda_handler(event, lambda_context)
        
        # Assert
        assert response['statusCode'] == 200
        body = json.loads(response['body'])
        # Should not contain path traversal
        assert '../' not in body['key']
        assert 'passwd.jpg' in body['key']
