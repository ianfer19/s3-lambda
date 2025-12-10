"""
File utility functions
"""
from datetime import datetime
from validators.file_validator import FileNameValidator


def sanitize_filename(filename: str) -> str:
    """
    Sanitize filename to prevent security issues
    
    Args:
        filename: Original filename
        
    Returns:
        Sanitized filename
    """
    return FileNameValidator.sanitize(filename)


def generate_unique_key(filename: str, folder_prefix: str = 'projects') -> str:
    """
    Generate a unique S3 key with timestamp
    
    Args:
        filename: Sanitized filename
        folder_prefix: Folder prefix for organization
        
    Returns:
        Unique S3 key
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
    return f"{folder_prefix}/{unique_name}"
