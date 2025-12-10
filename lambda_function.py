"""
Lambda function to generate presigned URLs for S3 uploads
Refactored with clean architecture principles
"""
import json
from typing import Dict, Any

from config.config import Config
from repositories.s3_repository import S3RepositoryImpl
from services.presigned_url_service import PresignedUrlService
from validators.file_validator import RequestValidator
from utils.http_responses import ResponseBuilder
from domain.exceptions import ValidationError, InvalidContentTypeError, S3OperationError


# Initialize configuration
Config.validate()

# Initialize dependencies
s3_repository = S3RepositoryImpl(bucket_name=Config.S3_BUCKET_NAME)
presigned_url_service = PresignedUrlService(
    s3_repository=s3_repository,
    folder_prefix=Config.S3_FOLDER_PREFIX,
    url_expiration=Config.PRESIGNED_URL_EXPIRATION
)


def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
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
    
    try:
        # Handle OPTIONS request for CORS preflight
        if event.get('httpMethod') == 'OPTIONS':
            return ResponseBuilder.cors_preflight()
        
        # Parse request body
        body = json.loads(event.get('body', '{}'))
        
        # Validate and parse request
        request = RequestValidator.validate_presigned_url_request(
            data=body,
            allowed_content_types=Config.ALLOWED_CONTENT_TYPES
        )
        
        # Generate presigned URL
        response = presigned_url_service.generate_upload_url(request)
        
        # Return success response
        return ResponseBuilder.success(response.to_dict())
        
    except json.JSONDecodeError:
        return ResponseBuilder.error(
            message='Invalid JSON in request body',
            status_code=400
        )
    
    except ValidationError as e:
        return ResponseBuilder.error(
            message=e.message,
            status_code=400,
            field=e.field
        )
    
    except InvalidContentTypeError as e:
        return ResponseBuilder.error(
            message=e.message,
            status_code=400,
            field=e.field
        )
    
    except S3OperationError as e:
        # Log the error (CloudWatch will capture print statements)
        print(f"S3 operation error: {e.message}")
        return ResponseBuilder.error(
            message='Failed to generate upload URL',
            status_code=500
        )
    
    except Exception as e:
        # Log unexpected errors
        print(f"Unexpected error: {str(e)}")
        return ResponseBuilder.error(
            message='Internal server error',
            status_code=500
        )