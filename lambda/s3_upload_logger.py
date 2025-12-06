"""
S3 Upload Logger Lambda Function
================================
This Lambda function is triggered by S3 ObjectCreated events and logs
file upload details to CloudWatch Logs.

Author: Your Name
Course: Cloud Computing
Date: December 2024
"""

import json
import logging
import os
from datetime import datetime

# Configure logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)


def lambda_handler(event, context):
    """
    Main Lambda handler function.
    
    Args:
        event: S3 event notification containing upload details
        context: Lambda context object
    
    Returns:
        dict: Response with status code and message
    """
    project_name = os.environ.get('PROJECT_NAME', 'job-portal')
    environment = os.environ.get('ENVIRONMENT', 'dev')
    
    logger.info(f"[{project_name}] S3 Upload Event Received")
    logger.info(f"Full Event: {json.dumps(event, indent=2)}")
    
    processed_records = []
    
    # Process each record in the event
    for record in event.get('Records', []):
        try:
            # Extract S3 event details
            s3_info = record.get('s3', {})
            bucket_name = s3_info.get('bucket', {}).get('name', 'Unknown')
            object_key = s3_info.get('object', {}).get('key', 'Unknown')
            object_size = s3_info.get('object', {}).get('size', 0)
            event_time = record.get('eventTime', datetime.now().isoformat())
            event_name = record.get('eventName', 'Unknown')
            
            # Create structured log entry
            log_entry = {
                'timestamp': event_time,
                'project': project_name,
                'environment': environment,
                'event_type': event_name,
                'bucket': bucket_name,
                'object_key': object_key,
                'object_size_bytes': object_size,
                'object_size_readable': format_size(object_size),
                'source_ip': record.get('requestParameters', {}).get('sourceIPAddress', 'Unknown'),
                'user_identity': record.get('userIdentity', {}).get('principalId', 'Unknown')
            }
            
            # Log the structured information
            logger.info("=" * 60)
            logger.info("S3 UPLOAD EVENT DETAILS")
            logger.info("=" * 60)
            logger.info(f"Timestamp: {log_entry['timestamp']}")
            logger.info(f"Bucket: {log_entry['bucket']}")
            logger.info(f"Object Key: {log_entry['object_key']}")
            logger.info(f"Size: {log_entry['object_size_readable']} ({log_entry['object_size_bytes']} bytes)")
            logger.info(f"Event Type: {log_entry['event_type']}")
            logger.info(f"Source IP: {log_entry['source_ip']}")
            
            # Categorize file type
            file_extension = object_key.split('.')[-1].lower() if '.' in object_key else 'unknown'
            file_category = categorize_file(file_extension)
            logger.info(f"File Category: {file_category}")
            logger.info(f"File Extension: {file_extension}")
            logger.info("=" * 60)
            
            processed_records.append({
                'bucket': bucket_name,
                'key': object_key,
                'category': file_category
            })
            
        except Exception as e:
            logger.error(f"Error processing record: {str(e)}")
            logger.error(f"Record: {json.dumps(record, indent=2)}")
    
    response = {
        'statusCode': 200,
        'body': json.dumps({
            'message': 'S3 upload event(s) logged successfully',
            'records_processed': len(processed_records),
            'details': processed_records
        })
    }
    
    logger.info(f"Lambda Response: {json.dumps(response, indent=2)}")
    return response


def format_size(size_bytes):
    """
    Convert bytes to human readable format.
    
    Args:
        size_bytes: Size in bytes
    
    Returns:
        str: Human readable size string
    """
    if size_bytes == 0:
        return "0 B"
    
    size_names = ("B", "KB", "MB", "GB", "TB")
    i = 0
    while size_bytes >= 1024 and i < len(size_names) - 1:
        size_bytes /= 1024
        i += 1
    
    return f"{size_bytes:.2f} {size_names[i]}"


def categorize_file(extension):
    """
    Categorize file based on its extension.
    
    Args:
        extension: File extension (without dot)
    
    Returns:
        str: Category name
    """
    categories = {
        'resume': ['pdf', 'doc', 'docx', 'txt', 'rtf', 'odt'],
        'image': ['jpg', 'jpeg', 'png', 'gif', 'webp', 'svg', 'bmp', 'ico'],
        'data': ['csv', 'xlsx', 'xls', 'json', 'xml', 'yaml', 'yml'],
        'archive': ['zip', 'tar', 'gz', 'rar', '7z'],
        'video': ['mp4', 'avi', 'mov', 'mkv', 'webm'],
        'audio': ['mp3', 'wav', 'flac', 'aac', 'ogg']
    }
    
    for category, extensions in categories.items():
        if extension.lower() in extensions:
            return category
    
    return 'other'


# For local testing
if __name__ == "__main__":
    # Sample S3 event for testing
    test_event = {
        "Records": [
            {
                "eventTime": "2024-12-01T12:00:00.000Z",
                "eventName": "ObjectCreated:Put",
                "s3": {
                    "bucket": {
                        "name": "job-portal-dev-files"
                    },
                    "object": {
                        "key": "resumes/john_doe_resume.pdf",
                        "size": 1024567
                    }
                },
                "requestParameters": {
                    "sourceIPAddress": "192.168.1.100"
                },
                "userIdentity": {
                    "principalId": "EXAMPLE123"
                }
            }
        ]
    }
    
    # Test the handler
    result = lambda_handler(test_event, None)
    print(f"\nTest Result: {json.dumps(result, indent=2)}")
