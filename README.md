# S3 Presigned URL Lambda Function

AWS Lambda function to generate presigned URLs for uploading images to S3.

## Features

- Generates S3 Presigned URLs for secure direct uploads.
- Validates file names and content types.
- Sanitizes file names to prevent issues.
- Returns public URL for immediate access after upload.

## Critical: S3 CORS Configuration

For the frontend to upload files directly to S3 using the presigned URL, you **must** configure CORS on your S3 bucket. If you see `TypeError: Failed to fetch` or CORS errors in your browser console, this is the cause.

1. Go to the AWS S3 Console.
2. Select your bucket (`portafolio-iam-s3`).
3. Go to the **Permissions** tab.
4. Scroll down to **Cross-origin resource sharing (CORS)**.
5. Click **Edit** and paste the configuration found in `s3_cors_config.json`:

```json
[
    {
        "AllowedHeaders": [
            "*"
        ],
        "AllowedMethods": [
            "GET",
            "PUT",
            "POST",
            "HEAD"
        ],
        "AllowedOrigins": [
            "*"
        ],
        "ExposeHeaders": [
            "ETag"
        ],
        "MaxAgeSeconds": 3000
    }
]
```

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `S3_BUCKET_NAME` | S3 bucket name | `portafolio-iam-s3` |

## Deployment

1. Install dependencies:
   ```bash
   pip install -r requirements.txt -t .
   ```
2. Zip the function and dependencies:
   ```bash
   zip -r lambda.zip . -x "*.git*"
   ```
3. Upload to AWS Lambda.
