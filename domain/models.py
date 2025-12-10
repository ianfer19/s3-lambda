"""
Domain models for the S3 presigned URL service
"""
from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class PresignedUrlRequest:
    """
    Value object representing a request to generate a presigned URL
    """
    file_name: str
    content_type: str
    
    def __post_init__(self):
        """Validate required fields"""
        if not self.file_name:
            raise ValueError("file_name is required")
        if not self.content_type:
            raise ValueError("content_type is required")


@dataclass(frozen=True)
class S3FileMetadata:
    """
    Value object representing S3 file metadata
    """
    key: str
    content_type: str
    bucket: str
    
    @property
    def public_url(self) -> str:
        """Generate the public URL for the file"""
        return f"https://{self.bucket}.s3.amazonaws.com/{self.key}"


@dataclass(frozen=True)
class PresignedUrlResponse:
    """
    Value object representing the response with presigned URL
    """
    upload_url: str
    file_url: str
    key: str
    
    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization"""
        return {
            'uploadUrl': self.upload_url,
            'fileUrl': self.file_url,
            'key': self.key
        }
