"""
Cloud Storage service - handles GCS operations including signed URL generation
"""
from google.cloud import storage
from datetime import timedelta
import os
import time
import random
import string
from dotenv import load_dotenv

load_dotenv()
# Create a storage client
storage_client = storage.Client()

# The ID of your GCS bucket
BUCKET_NAME = os.getenv('GCS_BUCKET_NAME', 'query_bucket_for_manuals_rob')
print(os.getenv('GOOGLE_APPLICATION_CREDENTIALS'))


def generate_v4_upload_signed_url(file_name=None, content_type='application/octet-stream'):
    """
    Generates a v4 signed URL for uploading a file to Google Cloud Storage.
    
    The signed URL allows direct upload to GCS without exposing credentials.
    The URL is valid for 15 minutes.
    
    Args:
        file_name: Optional name for the file. If not provided, generates a unique name.
        content_type: The MIME type of the file (default: 'application/octet-stream')
        
    Returns:
        dict: Contains 'url' (the signed URL) and 'fileName' (the actual filename used)
        
    Example:
        result = generate_v4_upload_signed_url('document.pdf', 'application/pdf')
        # Upload to result['url'] with PUT request
    """
    try:
        # Generate a unique filename if not provided
        if not file_name:
            timestamp = int(time.time() * 1000)
            random_str = ''.join(random.choices(string.ascii_lowercase + string.digits, k=7))
            file_name = f'upload_{timestamp}_{random_str}'
        
        # Get the bucket and blob
        bucket = storage_client.bucket(BUCKET_NAME)
        blob = bucket.blob(file_name)
        
        # Generate a signed URL valid for 15 minutes
        url = blob.generate_signed_url(
            version='v4',
            expiration=timedelta(minutes=15),
            method='PUT',
            content_type=content_type
        )
        
        print(f'Generated PUT signed URL for file: {file_name} with contentType: {content_type}')
        print(f'URL: {url}')
        
        return {
            'url': url,
            'fileName': file_name
        }
    except Exception as e:
        print(f'Error generating signed URL: {e}')
        raise e