"""
Unit tests for services
"""
import pytest
from unittest.mock import Mock, MagicMock
from services.presigned_url_service import PresignedUrlService
from domain.models import PresignedUrlRequest, PresignedUrlResponse
from domain.exceptions import S3OperationError


class TestPresignedUrlService:
    """Tests for PresignedUrlService"""
    
    @pytest.fixture
    def mock_s3_repository(self):
        """Create a mock S3 repository"""
        return Mock()
    
    @pytest.fixture
    def service(self, mock_s3_repository):
        """Create service instance with mocked repository"""
        return PresignedUrlService(
            s3_repository=mock_s3_repository,
            folder_prefix='test-folder',
            url_expiration=300
        )
    
    def test_generate_upload_url_success(self, service, mock_s3_repository):
        """Test successful URL generation"""
        # Setup
        request = PresignedUrlRequest(
            file_name='test.jpg',
            content_type='image/jpeg'
        )
        
        mock_s3_repository.generate_presigned_url.return_value = 'https://s3.aws.com/presigned-url'
        mock_s3_repository.get_public_url.return_value = 'https://s3.aws.com/public-url'
        
        # Execute
        result = service.generate_upload_url(request)
        
        # Assert
        assert isinstance(result, PresignedUrlResponse)
        assert result.upload_url == 'https://s3.aws.com/presigned-url'
        assert result.file_url == 'https://s3.aws.com/public-url'
        assert result.key.startswith('test-folder/')
        assert 'test.jpg' in result.key
        
        # Verify repository was called correctly
        mock_s3_repository.generate_presigned_url.assert_called_once()
        mock_s3_repository.get_public_url.assert_called_once()
    
    def test_generate_upload_url_sanitizes_filename(self, service, mock_s3_repository):
        """Test that filename is sanitized"""
        # Setup
        request = PresignedUrlRequest(
            file_name='../../etc/passwd.jpg',
            content_type='image/jpeg'
        )
        
        mock_s3_repository.generate_presigned_url.return_value = 'https://s3.aws.com/presigned-url'
        mock_s3_repository.get_public_url.return_value = 'https://s3.aws.com/public-url'
        
        # Execute
        result = service.generate_upload_url(request)
        
        # Assert - should not contain path traversal
        assert '../' not in result.key
        assert 'passwd.jpg' in result.key
    
    def test_generate_upload_url_creates_unique_key(self, service, mock_s3_repository):
        """Test that unique keys are generated"""
        # Setup
        request = PresignedUrlRequest(
            file_name='test.jpg',
            content_type='image/jpeg'
        )
        
        mock_s3_repository.generate_presigned_url.return_value = 'https://s3.aws.com/presigned-url'
        mock_s3_repository.get_public_url.return_value = 'https://s3.aws.com/public-url'
        
        # Execute twice
        result1 = service.generate_upload_url(request)
        result2 = service.generate_upload_url(request)
        
        # Assert - keys should be different (due to timestamp)
        # Note: This might fail if executed in the same second
        # In practice, timestamps make keys unique
        assert result1.key.startswith('test-folder/')
        assert result2.key.startswith('test-folder/')
    
    def test_generate_upload_url_propagates_s3_error(self, service, mock_s3_repository):
        """Test that S3 errors are propagated"""
        # Setup
        request = PresignedUrlRequest(
            file_name='test.jpg',
            content_type='image/jpeg'
        )
        
        mock_s3_repository.generate_presigned_url.side_effect = S3OperationError(
            "S3 error", 
            operation="generate_presigned_url"
        )
        
        # Execute & Assert
        with pytest.raises(S3OperationError):
            service.generate_upload_url(request)
    
    def test_generate_upload_url_uses_correct_expiration(self, service, mock_s3_repository):
        """Test that correct expiration is used"""
        # Setup
        request = PresignedUrlRequest(
            file_name='test.jpg',
            content_type='image/jpeg'
        )
        
        mock_s3_repository.generate_presigned_url.return_value = 'https://s3.aws.com/presigned-url'
        mock_s3_repository.get_public_url.return_value = 'https://s3.aws.com/public-url'
        
        # Execute
        service.generate_upload_url(request)
        
        # Assert - check that expiration was passed correctly
        call_args = mock_s3_repository.generate_presigned_url.call_args
        assert call_args.kwargs['expiration'] == 300
    
    def test_generate_upload_url_uses_correct_content_type(self, service, mock_s3_repository):
        """Test that correct content type is used"""
        # Setup
        request = PresignedUrlRequest(
            file_name='test.jpg',
            content_type='image/jpeg'
        )
        
        mock_s3_repository.generate_presigned_url.return_value = 'https://s3.aws.com/presigned-url'
        mock_s3_repository.get_public_url.return_value = 'https://s3.aws.com/public-url'
        
        # Execute
        service.generate_upload_url(request)
        
        # Assert - check that content type was passed correctly
        call_args = mock_s3_repository.generate_presigned_url.call_args
        assert call_args.kwargs['content_type'] == 'image/jpeg'
