"""
Service layer for presigned URL generation
"""
from domain.models import PresignedUrlRequest, PresignedUrlResponse
from repositories.s3_repository import S3Repository
from utils.file_utils import sanitize_filename, generate_unique_key


class PresignedUrlService:
    """
    Service for generating presigned URLs for S3 uploads
    """
    
    def __init__(
        self, 
        s3_repository: S3Repository,
        folder_prefix: str,
        url_expiration: int
    ):
        """
        Initialize the service
        
        Args:
            s3_repository: S3 repository instance
            folder_prefix: Folder prefix for S3 keys
            url_expiration: Presigned URL expiration time in seconds
        """
        self.s3_repository = s3_repository
        self.folder_prefix = folder_prefix
        self.url_expiration = url_expiration
    
    def generate_upload_url(self, request: PresignedUrlRequest) -> PresignedUrlResponse:
        """
        Generate a presigned URL for file upload
        
        Args:
            request: Presigned URL request object
            
        Returns:
            PresignedUrlResponse with upload URL and file metadata
            
        Raises:
            S3OperationError: If S3 operations fail
        """
        # Sanitize filename
        sanitized_name = sanitize_filename(request.file_name)
        
        # Generate unique S3 key
        unique_key = generate_unique_key(sanitized_name, self.folder_prefix)
        
        # Generate presigned URL
        upload_url = self.s3_repository.generate_presigned_url(
            key=unique_key,
            content_type=request.content_type,
            expiration=self.url_expiration
        )
        
        # Get public URL
        file_url = self.s3_repository.get_public_url(unique_key)
        
        # Return response
        return PresignedUrlResponse(
            upload_url=upload_url,
            file_url=file_url,
            key=unique_key
        )
