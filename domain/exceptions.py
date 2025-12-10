"""
Domain exceptions for the S3 presigned URL service
"""


class DomainException(Exception):
    """Base exception for domain-level errors"""
    pass


class ValidationError(DomainException):
    """Raised when input validation fails"""
    
    def __init__(self, message: str, field: str = None):
        self.message = message
        self.field = field
        super().__init__(self.message)


class InvalidContentTypeError(ValidationError):
    """Raised when an unsupported content type is provided"""
    
    def __init__(self, content_type: str, allowed_types: list):
        message = f"Invalid content type '{content_type}'. Allowed types: {', '.join(allowed_types)}"
        super().__init__(message, field="contentType")
        self.content_type = content_type
        self.allowed_types = allowed_types


class S3OperationError(DomainException):
    """Raised when S3 operations fail"""
    
    def __init__(self, message: str, operation: str = None):
        self.message = message
        self.operation = operation
        super().__init__(self.message)
