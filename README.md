# S3 Presigned URL Lambda Function

AWS Lambda function to generate presigned URLs for uploading images to S3, refactored with clean architecture principles.

## Architecture

This Lambda function follows clean architecture principles with clear separation of concerns:

```
s3-lambda/
├── domain/                 # Domain layer (entities, value objects, exceptions)
│   ├── models.py          # Domain models (PresignedUrlRequest, PresignedUrlResponse, S3FileMetadata)
│   └── exceptions.py      # Custom domain exceptions
├── validators/            # Input validation layer
│   └── file_validator.py # File name, content type, and request validators
├── repositories/          # Data access layer
│   └── s3_repository.py  # S3 operations abstraction
├── services/              # Business logic layer
│   └── presigned_url_service.py  # Presigned URL generation service
├── config/                # Configuration layer
│   └── config.py         # Centralized configuration
├── utils/                 # Utility functions
│   ├── file_utils.py     # File name sanitization and key generation
│   └── http_responses.py # HTTP response builders
├── tests/                 # Test suite
│   ├── unit/             # Unit tests
│   │   ├── test_validators.py
│   │   ├── test_services.py
│   │   └── test_repositories.py
│   ├── integration/      # Integration tests
│   │   └── test_lambda_handler.py
│   └── conftest.py       # Pytest fixtures
└── lambda_function.py     # Lambda handler (thin orchestration layer)
```

## Features

- **Clean Architecture**: Separation of concerns with domain, repository, service, and handler layers
- **Type Safety**: Uses Python dataclasses for immutable domain models
- **Input Validation**: Comprehensive validation for file names and content types
- **Security**: File name sanitization to prevent path traversal attacks
- **Error Handling**: Custom exceptions with proper error messages
- **CORS Support**: Built-in CORS headers for frontend integration
- **Testability**: Dependency injection enables easy mocking and testing
- **Comprehensive Tests**: Unit and integration tests with >80% coverage

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `S3_BUCKET_NAME` | S3 bucket name | `portafolio-iam-s3` |
| `PRESIGNED_URL_EXPIRATION` | URL expiration in seconds | `300` (5 minutes) |
| `S3_FOLDER_PREFIX` | Folder prefix for uploads | `projects` |
| `CORS_ALLOW_ORIGIN` | CORS allowed origin | `*` |

## API

### Request

**Method**: `POST`

**Body**:
```json
{
  "fileName": "example.jpg",
  "contentType": "image/jpeg"
}
```

### Response

**Success (200)**:
```json
{
  "uploadUrl": "https://s3.amazonaws.com/...",
  "fileUrl": "https://s3.amazonaws.com/bucket/key",
  "key": "projects/filename_timestamp.jpg"
}
```

**Error (400/500)**:
```json
{
  "error": "Error message",
  "field": "fieldName"  // Optional
}
```

## Allowed Content Types

- `image/jpeg`
- `image/jpg`
- `image/png`
- `image/gif`
- `image/webp`

## Development

### Install Dependencies

```bash
# Production dependencies
pip install -r requirements.txt

# Development dependencies (includes testing tools)
pip install -r requirements-dev.txt
```

### Run Tests

```bash
# Run all tests with coverage
pytest tests/ -v --cov=. --cov-report=term-missing

# Run only unit tests
pytest tests/unit/ -v

# Run only integration tests
pytest tests/integration/ -v

# Generate HTML coverage report
pytest tests/ --cov=. --cov-report=html
```

### Test Coverage

The test suite includes:
- **Validator Tests**: File name sanitization, content type validation, request validation
- **Service Tests**: Business logic with mocked dependencies
- **Repository Tests**: S3 operations with moto (AWS mocking)
- **Integration Tests**: End-to-end Lambda handler testing

## Deployment

1. Package the Lambda function:
```bash
zip -r lambda.zip . -x "tests/*" "*.pyc" "__pycache__/*" ".git/*"
```

2. Deploy to AWS Lambda with the following configuration:
   - Runtime: Python 3.9+
   - Handler: `lambda_function.lambda_handler`
   - Timeout: 30 seconds
   - Memory: 256 MB
   - IAM Role: Permissions for `s3:PutObject` and `s3:PutObjectAcl`

## Clean Code Principles Applied

1. **Single Responsibility**: Each class/module has one reason to change
2. **Dependency Inversion**: High-level modules don't depend on low-level modules
3. **Open/Closed**: Open for extension, closed for modification (repository pattern)
4. **Interface Segregation**: Small, focused interfaces
5. **DRY**: No code duplication
6. **SOLID**: All SOLID principles followed
7. **Testability**: Dependency injection enables easy testing

## Security Features

- File name sanitization (prevents path traversal)
- Content type validation (only allows images)
- File size limits (enforced by S3)
- Presigned URL expiration (5 minutes default)
- Public read ACL (configurable)
