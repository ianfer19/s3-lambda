"""
Configuration for the S3 presigned URL service
"""
import os
from typing import List


class Config:
    """
    Centralized configuration for the Lambda function
    """
    
    # S3 Configuration
    S3_BUCKET_NAME: str = os.environ.get('S3_BUCKET_NAME', 'portafolio-iam-s3')
    
    # Allowed content types for uploads
    ALLOWED_CONTENT_TYPES: List[str] = [
        'image/jpeg',
        'image/jpg',
        'image/png',
        'image/gif',
        'image/webp'
    ]
    
    # Presigned URL expiration time (in seconds)
    PRESIGNED_URL_EXPIRATION: int = int(os.environ.get('PRESIGNED_URL_EXPIRATION', '300'))
    
    # S3 folder prefix for uploaded files
    S3_FOLDER_PREFIX: str = os.environ.get('S3_FOLDER_PREFIX', 'projects')
    
    # CORS Configuration
    CORS_ALLOW_ORIGIN: str = os.environ.get('CORS_ALLOW_ORIGIN', '*')
    CORS_ALLOW_HEADERS: str = 'Content-Type,Authorization'
    CORS_ALLOW_METHODS: str = 'POST,OPTIONS'
    
    @classmethod
    def validate(cls) -> None:
        """
        Validate that required configuration is present
        """
        if not cls.S3_BUCKET_NAME:
            raise ValueError("S3_BUCKET_NAME must be configured")
        
        if cls.PRESIGNED_URL_EXPIRATION <= 0:
            raise ValueError("PRESIGNED_URL_EXPIRATION must be positive")
    
    @classmethod
    def get_cors_headers(cls) -> dict:
        """
        Get standardized CORS headers
        """
        return {
            'Access-Control-Allow-Origin': cls.CORS_ALLOW_ORIGIN,
            'Access-Control-Allow-Headers': cls.CORS_ALLOW_HEADERS,
            'Access-Control-Allow-Methods': cls.CORS_ALLOW_METHODS
        }
