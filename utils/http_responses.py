"""
HTTP response builders
"""
import json
from typing import Any, Dict, Optional
from config.config import Config


class ResponseBuilder:
    """
    Builds standardized HTTP responses
    """
    
    @staticmethod
    def success(data: Any, status_code: int = 200) -> Dict:
        """
        Build a successful response
        
        Args:
            data: Response data (will be JSON serialized)
            status_code: HTTP status code
            
        Returns:
            Lambda response dictionary
        """
        return {
            'statusCode': status_code,
            'headers': Config.get_cors_headers(),
            'body': json.dumps(data)
        }
    
    @staticmethod
    def error(message: str, status_code: int = 500, field: Optional[str] = None) -> Dict:
        """
        Build an error response
        
        Args:
            message: Error message
            status_code: HTTP status code
            field: Optional field name that caused the error
            
        Returns:
            Lambda response dictionary
        """
        error_body = {'error': message}
        if field:
            error_body['field'] = field
        
        return {
            'statusCode': status_code,
            'headers': Config.get_cors_headers(),
            'body': json.dumps(error_body)
        }
    
    @staticmethod
    def cors_preflight() -> Dict:
        """
        Build a CORS preflight response
        
        Returns:
            Lambda response dictionary for OPTIONS request
        """
        return {
            'statusCode': 200,
            'headers': Config.get_cors_headers(),
            'body': json.dumps({'message': 'OK'})
        }
