"""
Validators for the S3 presigned URL service
"""
import re
from typing import List, Optional
from domain.exceptions import ValidationError, InvalidContentTypeError
from domain.models import PresignedUrlRequest


class FileNameValidator:
    """
    Validates and sanitizes file names
    """
    
    # Pattern to match valid characters (alphanumeric, dots, hyphens, underscores)
    VALID_CHARS_PATTERN = re.compile(r'[^a-zA-Z0-9._-]')
    
    # Maximum file name length
    MAX_FILENAME_LENGTH = 255
    
    @classmethod
    def sanitize(cls, filename: str) -> str:
        """
        Sanitize filename to prevent security issues
        
        Args:
            filename: Original filename
            
        Returns:
            Sanitized filename
            
        Raises:
            ValidationError: If filename is invalid
        """
        if not filename or not filename.strip():
            raise ValidationError("Filename cannot be empty", field="fileName")
        
        # Remove path components (prevent directory traversal)
        base_name = filename.split('/')[-1].split('\\')[-1]
        
        if not base_name:
            raise ValidationError("Invalid filename", field="fileName")
        
        # Replace invalid characters with underscores
        sanitized = cls.VALID_CHARS_PATTERN.sub('_', base_name)
        
        # Remove only leading dots (hidden files) and trim spaces
        # Don't strip trailing dots as they might be part of the extension
        sanitized = sanitized.lstrip('.').strip()
        
        if not sanitized:
            raise ValidationError("Filename contains only invalid characters", field="fileName")
        
        # Truncate if too long
        if len(sanitized) > cls.MAX_FILENAME_LENGTH:
            # Preserve extension if present
            if '.' in sanitized:
                name, ext = sanitized.rsplit('.', 1)
                max_name_length = cls.MAX_FILENAME_LENGTH - len(ext) - 1
                sanitized = f"{name[:max_name_length]}.{ext}"
            else:
                sanitized = sanitized[:cls.MAX_FILENAME_LENGTH]
        
        return sanitized
    
    @classmethod
    def validate(cls, filename: str) -> None:
        """
        Validate filename
        
        Args:
            filename: Filename to validate
            
        Raises:
            ValidationError: If filename is invalid
        """
        cls.sanitize(filename)  # Will raise if invalid


class ContentTypeValidator:
    """
    Validates content types
    """
    
    @classmethod
    def validate(cls, content_type: str, allowed_types: List[str]) -> None:
        """
        Validate that content type is allowed
        
        Args:
            content_type: Content type to validate
            allowed_types: List of allowed content types
            
        Raises:
            InvalidContentTypeError: If content type is not allowed
        """
        if not content_type or not content_type.strip():
            raise ValidationError("Content type cannot be empty", field="contentType")
        
        # Normalize to lowercase for comparison
        normalized_type = content_type.lower().strip()
        normalized_allowed = [t.lower() for t in allowed_types]
        
        if normalized_type not in normalized_allowed:
            raise InvalidContentTypeError(content_type, allowed_types)


class RequestValidator:
    """
    Validates complete request payloads
    """
    
    @classmethod
    def validate_presigned_url_request(
        cls, 
        data: dict, 
        allowed_content_types: List[str]
    ) -> PresignedUrlRequest:
        """
        Validate and parse presigned URL request
        
        Args:
            data: Request data dictionary
            allowed_content_types: List of allowed content types
            
        Returns:
            PresignedUrlRequest object
            
        Raises:
            ValidationError: If request is invalid
        """
        # Extract fields
        file_name = data.get('fileName')
        content_type = data.get('contentType')
        
        # Check required fields
        if not file_name:
            raise ValidationError("fileName is required", field="fileName")
        
        if not content_type:
            raise ValidationError("contentType is required", field="contentType")
        
        # Validate individual fields
        FileNameValidator.validate(file_name)
        ContentTypeValidator.validate(content_type, allowed_content_types)
        
        # Create and return request object
        return PresignedUrlRequest(
            file_name=file_name,
            content_type=content_type
        )
