# Media Storage Configuration Guide

This guide explains how to configure different cloud storage providers for the Eddits application.

## Overview

The Eddits application supports multiple storage backends:
- **Local Storage** (Development only)
- **AWS S3** (Recommended for production)
- **Google Cloud Storage**
- **DigitalOcean Spaces**

## Local Storage (Development)

Local storage is the default configuration for development environments.

### Configuration

In your `.env` file:
```env
STORAGE_TYPE=local
```

### Features
- Files stored in `media/` directory
- Direct file access via Django's media URL
- No additional setup required
- **Not recommended for production**

## AWS S3 Configuration

### Prerequisites

1. **AWS Account**: Create an AWS account at https://aws.amazon.com/
2. **S3 Bucket**: Create an S3 bucket for media storage
3. **IAM User**: Create an IAM user with S3 permissions

### Step 1: Create S3 Bucket

1. Go to AWS S3 Console
2. Click "Create bucket"
3. Choose a unique bucket name (e.g., `eddits-media-production`)
4. Select your preferred region
5. Configure bucket settings:
   - **Block all public access**: Keep enabled for security
   - **Bucket versioning**: Optional
   - **Server-side encryption**: Recommended

### Step 2: Create IAM User

1. Go to AWS IAM Console
2. Create a new user with programmatic access
3. Attach the following policy:

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "s3:GetObject",
                "s3:PutObject",
                "s3:DeleteObject",
                "s3:ListBucket"
            ],
            "Resource": [
                "arn:aws:s3:::your-bucket-name",
                "arn:aws:s3:::your-bucket-name/*"
            ]
        }
    ]
}
```

### Step 3: Environment Configuration

Update your `.env` file:

```env
# Storage Configuration
STORAGE_TYPE=aws

# AWS S3 Configuration
AWS_ACCESS_KEY_ID=your_access_key_id
AWS_SECRET_ACCESS_KEY=your_secret_access_key
AWS_STORAGE_BUCKET_NAME=your-bucket-name
AWS_S3_REGION_NAME=us-east-1
AWS_S3_CUSTOM_DOMAIN=  # Optional: CloudFront domain
```

### Step 4: Install Dependencies

Ensure boto3 is installed:
```bash
pip install boto3
```

## Google Cloud Storage Configuration

### Prerequisites

1. **Google Cloud Account**: Create account at https://cloud.google.com/
2. **Project**: Create or select a GCP project
3. **Storage Bucket**: Create a Cloud Storage bucket
4. **Service Account**: Create service account with Storage permissions

### Step 1: Create Storage Bucket

1. Go to Google Cloud Console
2. Navigate to Cloud Storage
3. Create a new bucket:
   - Choose unique name
   - Select location
   - Choose storage class (Standard recommended)
   - Set access control to "Uniform"

### Step 2: Create Service Account

1. Go to IAM & Admin > Service Accounts
2. Create new service account
3. Grant roles:
   - Storage Object Admin
   - Storage Legacy Bucket Reader
4. Create and download JSON key file

### Step 3: Environment Configuration

Update your `.env` file:

```env
# Storage Configuration
STORAGE_TYPE=gcp

# Google Cloud Storage Configuration
GS_BUCKET_NAME=your-bucket-name
GS_PROJECT_ID=your-project-id
GS_CREDENTIALS=/path/to/service-account-key.json
```

### Step 4: Install Dependencies

```bash
pip install google-cloud-storage
```

## DigitalOcean Spaces Configuration

DigitalOcean Spaces is S3-compatible, so we use the S3 backend with DO endpoints.

### Prerequisites

1. **DigitalOcean Account**: Create account at https://digitalocean.com/
2. **Spaces**: Create a Space (object storage)
3. **API Keys**: Generate Spaces access keys

### Step 1: Create Space

1. Go to DigitalOcean Control Panel
2. Navigate to Spaces
3. Create new Space:
   - Choose datacenter region
   - Set unique name
   - Choose CDN option (recommended)

### Step 2: Generate API Keys

1. Go to API section in control panel
2. Generate new Spaces access key
3. Note down the key and secret

### Step 3: Environment Configuration

Update your `.env` file:

```env
# Storage Configuration
STORAGE_TYPE=aws  # Use AWS backend for DO Spaces

# DigitalOcean Spaces Configuration
AWS_ACCESS_KEY_ID=your_spaces_key
AWS_SECRET_ACCESS_KEY=your_spaces_secret
AWS_STORAGE_BUCKET_NAME=your-space-name
AWS_S3_REGION_NAME=nyc3  # or your chosen region
AWS_S3_ENDPOINT_URL=https://nyc3.digitaloceanspaces.com  # region-specific
AWS_S3_CUSTOM_DOMAIN=your-space-name.nyc3.cdn.digitaloceanspaces.com  # if using CDN
```

### Step 4: Update Storage Backend

For DigitalOcean Spaces, update `storage_backends.py` to include endpoint URL:

```python
class S3MediaStorage(S3Boto3Storage, MediaStorage):
    bucket_name = settings.AWS_STORAGE_BUCKET_NAME
    region_name = settings.AWS_S3_REGION_NAME
    custom_domain = settings.AWS_S3_CUSTOM_DOMAIN
    endpoint_url = getattr(settings, 'AWS_S3_ENDPOINT_URL', None)  # Add this line
    file_overwrite = False
    default_acl = 'private'
```

## Security Best Practices

### 1. Access Control
- Use private buckets/containers
- Generate signed URLs for file access
- Implement proper authentication

### 2. Environment Variables
- Never commit credentials to version control
- Use environment variables for all sensitive data
- Rotate access keys regularly

### 3. CORS Configuration

For web uploads, configure CORS on your storage bucket:

**AWS S3 CORS:**
```json
[
    {
        "AllowedHeaders": ["*"],
        "AllowedMethods": ["GET", "PUT", "POST", "DELETE"],
        "AllowedOrigins": ["https://yourdomain.com"],
        "ExposeHeaders": ["ETag"]
    }
]
```

**Google Cloud Storage CORS:**
```json
[
    {
        "origin": ["https://yourdomain.com"],
        "method": ["GET", "PUT", "POST", "DELETE"],
        "responseHeader": ["Content-Type"],
        "maxAgeSeconds": 3600
    }
]
```

## Testing Storage Configuration

### 1. Test Upload

Use the Django shell to test file upload:

```python
from media_manager import media_manager
from django.core.files.base import ContentFile

# Create test file
test_file = ContentFile(b'test content', name='test.txt')

# Test upload
result = media_manager.upload_file(test_file)
print(result)
```

### 2. Test Signed URLs

```python
from media_manager import media_manager

# Test signed URL generation
signed_url = media_manager.get_signed_url('test/file.jpg')
print(signed_url)
```

### 3. API Testing

Test the media upload API:

```bash
# Upload file
curl -X POST \
  http://localhost:8000/api/media/upload/ \
  -H 'Authorization: Bearer your_jwt_token' \
  -F 'files=@/path/to/image.jpg' \
  -F 'event_id=1' \
  -F 'file_type=photo'

# Get storage stats
curl -X GET \
  http://localhost:8000/api/media/stats/ \
  -H 'Authorization: Bearer your_jwt_token'
```

## Monitoring and Maintenance

### 1. Storage Usage
- Monitor storage usage through the admin dashboard
- Set up alerts for storage quotas
- Implement cleanup policies for old files

### 2. Performance
- Use CDN for faster file delivery
- Implement caching for frequently accessed files
- Monitor upload/download speeds

### 3. Backup
- Enable versioning on storage buckets
- Implement cross-region replication
- Regular backup verification

## Troubleshooting

### Common Issues

1. **Permission Denied**
   - Check IAM policies/permissions
   - Verify access keys
   - Ensure bucket exists

2. **CORS Errors**
   - Configure CORS on storage bucket
   - Check allowed origins
   - Verify request headers

3. **Signed URL Issues**
   - Check clock synchronization
   - Verify credentials
   - Check URL expiration

4. **Upload Failures**
   - Check file size limits
   - Verify file format support
   - Check network connectivity

### Debug Mode

Enable debug logging in `settings.py`:

```python
LOGGING = {
    'loggers': {
        'media_manager': {
            'handlers': ['console'],
            'level': 'DEBUG',
            'propagate': False,
        },
        'storages': {
            'handlers': ['console'],
            'level': 'DEBUG',
            'propagate': False,
        },
    },
}
```

## Cost Optimization

### 1. Storage Classes
- Use appropriate storage classes (Standard, IA, Archive)
- Implement lifecycle policies
- Regular cleanup of unused files

### 2. Transfer Optimization
- Compress images before upload
- Use efficient file formats
- Implement progressive upload for large files

### 3. CDN Usage
- Use CloudFront (AWS) or Cloud CDN (GCP)
- Cache static content
- Optimize cache headers

This completes the storage configuration guide. Choose the storage provider that best fits your needs and follow the respective setup instructions.