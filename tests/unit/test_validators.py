"""
Unit tests for validators
"""
import pytest
from validators.file_validator import (
    FileNameValidator, 
    ContentTypeValidator, 
    RequestValidator
)
from domain.exceptions import ValidationError, InvalidContentTypeError
from domain.models import PresignedUrlRequest


class TestFileNameValidator:
    """Tests for FileNameValidator"""
    
    def test_sanitize_valid_filename(self):
        """Test sanitization of valid filename"""
        result = FileNameValidator.sanitize('test-image_123.jpg')
        assert result == 'test-image_123.jpg'
    
    def test_sanitize_filename_with_special_chars(self):
        """Test sanitization removes special characters"""
        result = FileNameValidator.sanitize('test@image#123$.jpg')
        assert result == 'test_image_123_.jpg'
    
    def test_sanitize_filename_with_path_traversal(self):
        """Test sanitization prevents path traversal"""
        result = FileNameValidator.sanitize('../../etc/passwd')
        assert result == 'passwd'
        
        result = FileNameValidator.sanitize('..\\..\\windows\\system32')
        assert result == 'system32'
    
    def test_sanitize_filename_with_spaces(self):
        """Test sanitization handles leading/trailing spaces and dots"""
        result = FileNameValidator.sanitize('  .test.jpg.  ')
        assert result == 'test.jpg'
    
    def test_sanitize_empty_filename_raises_error(self):
        """Test empty filename raises ValidationError"""
        with pytest.raises(ValidationError) as exc_info:
            FileNameValidator.sanitize('')
        assert exc_info.value.field == 'fileName'
    
    def test_sanitize_only_invalid_chars_raises_error(self):
        """Test filename with only invalid characters raises error"""
        with pytest.raises(ValidationError) as exc_info:
            FileNameValidator.sanitize('@#$%^&*()')
        assert 'invalid characters' in exc_info.value.message.lower()
    
    def test_sanitize_long_filename(self):
        """Test sanitization truncates long filenames"""
        long_name = 'a' * 300 + '.jpg'
        result = FileNameValidator.sanitize(long_name)
        assert len(result) <= 255
        assert result.endswith('.jpg')
    
    def test_validate_valid_filename(self):
        """Test validation passes for valid filename"""
        # Should not raise
        FileNameValidator.validate('test.jpg')
    
    def test_validate_invalid_filename_raises_error(self):
        """Test validation raises error for invalid filename"""
        with pytest.raises(ValidationError):
            FileNameValidator.validate('')


class TestContentTypeValidator:
    """Tests for ContentTypeValidator"""
    
    def test_validate_allowed_content_type(self, allowed_content_types):
        """Test validation passes for allowed content type"""
        # Should not raise
        ContentTypeValidator.validate('image/jpeg', allowed_content_types)
    
    def test_validate_case_insensitive(self, allowed_content_types):
        """Test validation is case insensitive"""
        # Should not raise
        ContentTypeValidator.validate('IMAGE/JPEG', allowed_content_types)
        ContentTypeValidator.validate('Image/Jpeg', allowed_content_types)
    
    def test_validate_disallowed_content_type_raises_error(self, allowed_content_types):
        """Test validation raises error for disallowed content type"""
        with pytest.raises(InvalidContentTypeError) as exc_info:
            ContentTypeValidator.validate('application/pdf', allowed_content_types)
        assert exc_info.value.content_type == 'application/pdf'
        assert exc_info.value.field == 'contentType'
    
    def test_validate_empty_content_type_raises_error(self, allowed_content_types):
        """Test validation raises error for empty content type"""
        with pytest.raises(ValidationError) as exc_info:
            ContentTypeValidator.validate('', allowed_content_types)
        assert exc_info.value.field == 'contentType'
    
    def test_validate_whitespace_content_type_raises_error(self, allowed_content_types):
        """Test validation raises error for whitespace-only content type"""
        with pytest.raises(ValidationError):
            ContentTypeValidator.validate('   ', allowed_content_types)


class TestRequestValidator:
    """Tests for RequestValidator"""
    
    def test_validate_valid_request(self, sample_request_data, allowed_content_types):
        """Test validation of valid request"""
        result = RequestValidator.validate_presigned_url_request(
            sample_request_data, 
            allowed_content_types
        )
        assert isinstance(result, PresignedUrlRequest)
        assert result.file_name == 'test-image.jpg'
        assert result.content_type == 'image/jpeg'
    
    def test_validate_missing_filename_raises_error(self, allowed_content_types):
        """Test validation raises error when fileName is missing"""
        data = {'contentType': 'image/jpeg'}
        with pytest.raises(ValidationError) as exc_info:
            RequestValidator.validate_presigned_url_request(data, allowed_content_types)
        assert exc_info.value.field == 'fileName'
    
    def test_validate_missing_content_type_raises_error(self, allowed_content_types):
        """Test validation raises error when contentType is missing"""
        data = {'fileName': 'test.jpg'}
        with pytest.raises(ValidationError) as exc_info:
            RequestValidator.validate_presigned_url_request(data, allowed_content_types)
        assert exc_info.value.field == 'contentType'
    
    def test_validate_invalid_content_type_raises_error(self, allowed_content_types):
        """Test validation raises error for invalid content type"""
        data = {
            'fileName': 'test.pdf',
            'contentType': 'application/pdf'
        }
        with pytest.raises(InvalidContentTypeError):
            RequestValidator.validate_presigned_url_request(data, allowed_content_types)
    
    def test_validate_empty_request_raises_error(self, allowed_content_types):
        """Test validation raises error for empty request"""
        with pytest.raises(ValidationError):
            RequestValidator.validate_presigned_url_request({}, allowed_content_types)
