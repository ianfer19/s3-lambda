"""
S3 Repository for handling S3 operations
"""
from abc import ABC, abstractmethod
import boto3
from botocore.exceptions import ClientError
from typing import Optional

from domain.models import S3FileMetadata
from domain.exceptions import S3OperationError


class S3Repository(ABC):
    """
    Abstract base class for S3 operations
    """
    
    @abstractmethod
    def generate_presigned_url(
        self, 
        key: str, 
        content_type: str, 
        expiration: int
    ) -> str:
        """
        Generate a presigned URL for uploading to S3
        
        Args:
            key: S3 object key
            content_type: Content type of the file
            expiration: URL expiration time in seconds
            
        Returns:
            Presigned URL string
            
        Raises:
            S3OperationError: If URL generation fails
        """
        pass
    
    @abstractmethod
    def get_public_url(self, key: str) -> str:
        """
        Get the public URL for an S3 object
        
        Args:
            key: S3 object key
            
        Returns:
            Public URL string
        """
        pass


class S3RepositoryImpl(S3Repository):
    """
    Concrete implementation of S3Repository using boto3
    """
    
    def __init__(self, bucket_name: str, s3_client: Optional[boto3.client] = None):
        """
        Initialize the repository
        
        Args:
            bucket_name: Name of the S3 bucket
            s3_client: Optional boto3 S3 client (for testing)
        """
        self.bucket_name = bucket_name
        self.s3_client = s3_client or boto3.client('s3')
    
    def generate_presigned_url(
        self, 
        key: str, 
        content_type: str, 
        expiration: int
    ) -> str:
        """
        Generate a presigned URL for uploading to S3
        
        Args:
            key: S3 object key
            content_type: Content type of the file
            expiration: URL expiration time in seconds
            
        Returns:
            Presigned URL string
            
        Raises:
            S3OperationError: If URL generation fails
        """
        try:
            presigned_url = self.s3_client.generate_presigned_url(
                'put_object',
                Params={
                    'Bucket': self.bucket_name,
                    'Key': key,
                    'ContentType': content_type,
                    'ACL': 'public-read'
                },
                ExpiresIn=expiration
            )
            return presigned_url
        except ClientError as e:
            error_message = f"Failed to generate presigned URL: {str(e)}"
            raise S3OperationError(error_message, operation="generate_presigned_url")
        except Exception as e:
            error_message = f"Unexpected error generating presigned URL: {str(e)}"
            raise S3OperationError(error_message, operation="generate_presigned_url")
    
    def get_public_url(self, key: str) -> str:
        """
        Get the public URL for an S3 object
        
        Args:
            key: S3 object key
            
        Returns:
            Public URL string
        """
        return f"https://{self.bucket_name}.s3.amazonaws.com/{key}"
    
    def create_file_metadata(self, key: str, content_type: str) -> S3FileMetadata:
        """
        Create S3 file metadata object
        
        Args:
            key: S3 object key
            content_type: Content type of the file
            
        Returns:
            S3FileMetadata object
        """
        return S3FileMetadata(
            key=key,
            content_type=content_type,
            bucket=self.bucket_name
        )
