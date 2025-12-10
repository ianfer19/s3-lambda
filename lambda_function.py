"""
Lambda function to generate presigned URLs for S3 uploads
This function allows the frontend to upload images directly to S3
"""
import json
import boto3
import os
from datetime import datetime
from botocore.exceptions import ClientError
# Initialize S3 client
s3_client = boto3.client('s3')
# Configuration
BUCKET_NAME = os.environ.get('S3_BUCKET_NAME', 'portafolio-iam-s3')
ALLOWED_CONTENT_TYPES = [
    'image/jpeg',
    'image/jpg',
    'image/png',
    'image/gif',
    'image/webp'
]
PRESIGNED_URL_EXPIRATION = 300  # 5 minutes
def lambda_handler(event, context):
    """
    Generate a presigned URL for uploading files to S3
    
    Expected request body:
    {
        "fileName": "example.jpg",
        "contentType": "image/jpeg"
    }
    
    Returns:
    {
        "uploadUrl": "https://s3.amazonaws.com/...",
        "fileUrl": "https://s3.amazonaws.com/bucket/key",
        "key": "projects/filename_timestamp.jpg"
    }
    """
    
    # CORS headers
    headers = {
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Headers': 'Content-Type,Authorization',
        'Access-Control-Allow-Methods': 'POST,OPTIONS'
    }
    
    try:
        # Handle OPTIONS request for CORS
        if event.get('httpMethod') == 'OPTIONS':
            return {
                'statusCode': 200,
                'headers': headers,
                'body': json.dumps({'message': 'OK'})
            }
        
        # Parse request body
        body = json.loads(event.get('body', '{}'))
        file_name = body.get('fileName')
        content_type = body.get('contentType')
        
        # Validate input
        if not file_name or not content_type:
            return {
                'statusCode': 400,
                'headers': headers,
                'body': json.dumps({
                    'error': 'fileName and contentType are required'
                })
            }
        
        # Validate content type
        if content_type.lower() not in ALLOWED_CONTENT_TYPES:
            return {
                'statusCode': 400,
                'headers': headers,
                'body': json.dumps({
                    'error': f'Invalid content type. Allowed types: {", ".join(ALLOWED_CONTENT_TYPES)}'
                })
            }
        
        # Sanitize and generate unique file name
        sanitized_name = sanitize_filename(file_name)
        unique_key = generate_unique_key(sanitized_name)
        
        # Generate presigned URL for PUT operation
        try:
            presigned_url = s3_client.generate_presigned_url(
                'put_object',
                Params={
                    'Bucket': BUCKET_NAME,
                    'Key': unique_key,
                    'ContentType': content_type
                },
                ExpiresIn=PRESIGNED_URL_EXPIRATION
            )
        except ClientError as e:
            print(f"Error generating presigned URL: {str(e)}")
            return {
                'statusCode': 500,
                'headers': headers,
                'body': json.dumps({
                    'error': 'Failed to generate upload URL'
                })
            }
        
        # Generate the public URL for the file
        file_url = f"https://{BUCKET_NAME}.s3.amazonaws.com/{unique_key}"
        
        # Return response
        return {
            'statusCode': 200,
            'headers': headers,
            'body': json.dumps({
                'uploadUrl': presigned_url,
                'fileUrl': file_url,
                'key': unique_key
            })
        }
        
    except json.JSONDecodeError:
        return {
            'statusCode': 400,
            'headers': headers,
            'body': json.dumps({
                'error': 'Invalid JSON in request body'
            })
        }
    except Exception as e:
        print(f"Unexpected error: {str(e)}")
        return {
            'statusCode': 500,
            'headers': headers,
            'body': json.dumps({
                'error': 'Internal server error'
            })
        }
def sanitize_filename(filename):
    """
    Sanitize filename to prevent security issues
    """
    # Remove path components
    base_name = filename.split('/')[-1].split('\\')[-1]
    
    # Remove special characters except dots, hyphens, and underscores
    sanitized = ''.join(c if c.isalnum() or c in '._-' else '_' for c in base_name)
    
    return sanitized
def generate_unique_key(filename):
    """
    Generate a unique S3 key with timestamp
    """
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    
    # Split filename and extension
    if '.' in filename:
        name_parts = filename.rsplit('.', 1)
        name = name_parts[0]
        extension = name_parts[1]
        unique_name = f"{name}_{timestamp}.{extension}"
    else:
        unique_name = f"{filename}_{timestamp}"
    
    # Add folder prefix for organization
    return f"projects/{unique_name}"