"""
S3 Operations Script using Boto3
================================
This script demonstrates S3 bucket creation, file upload, and listing operations
using the AWS SDK for Python (Boto3).

Author: Your Name
Course: Cloud Computing
Date: December 2024

Usage:
    python s3_operations.py
"""

import boto3
import json
import os
import sys
from datetime import datetime
from botocore.exceptions import ClientError

# Configuration
PROJECT_NAME = "job-portal"
ENVIRONMENT = "dev"
REGION = "us-east-1"


def create_s3_client():
    """Create and return an S3 client."""
    return boto3.client('s3', region_name=REGION)


def create_s3_resource():
    """Create and return an S3 resource."""
    return boto3.resource('s3', region_name=REGION)


def create_bucket(bucket_name):
    """
    Create an S3 bucket.
    
    Args:
        bucket_name: Name of the bucket to create
    
    Returns:
        bool: True if bucket was created successfully
    """
    s3_client = create_s3_client()
    
    try:
        # For us-east-1, don't specify LocationConstraint
        if REGION == 'us-east-1':
            s3_client.create_bucket(Bucket=bucket_name)
        else:
            s3_client.create_bucket(
                Bucket=bucket_name,
                CreateBucketConfiguration={'LocationConstraint': REGION}
            )
        
        print(f"✅ Bucket '{bucket_name}' created successfully!")
        
        # Enable versioning
        s3_client.put_bucket_versioning(
            Bucket=bucket_name,
            VersioningConfiguration={'Status': 'Enabled'}
        )
        print(f"✅ Versioning enabled for bucket '{bucket_name}'")
        
        # Add tags
        s3_client.put_bucket_tagging(
            Bucket=bucket_name,
            Tagging={
                'TagSet': [
                    {'Key': 'Project', 'Value': PROJECT_NAME},
                    {'Key': 'Environment', 'Value': ENVIRONMENT},
                    {'Key': 'ManagedBy', 'Value': 'boto3'}
                ]
            }
        )
        print(f"✅ Tags added to bucket '{bucket_name}'")
        
        return True
        
    except ClientError as e:
        error_code = e.response['Error']['Code']
        if error_code == 'BucketAlreadyOwnedByYou':
            print(f"ℹ️  Bucket '{bucket_name}' already exists and is owned by you.")
            return True
        elif error_code == 'BucketAlreadyExists':
            print(f"❌ Bucket name '{bucket_name}' is already taken globally.")
            return False
        else:
            print(f"❌ Error creating bucket: {e}")
            return False


def upload_file(bucket_name, file_path, object_key=None):
    """
    Upload a file to an S3 bucket.
    
    Args:
        bucket_name: Target bucket name
        file_path: Local path to the file
        object_key: S3 object key (optional, defaults to filename)
    
    Returns:
        bool: True if file was uploaded successfully
    """
    s3_client = create_s3_client()
    
    # Use filename as key if not specified
    if object_key is None:
        object_key = os.path.basename(file_path)
    
    try:
        # Upload with metadata
        extra_args = {
            'Metadata': {
                'uploaded-by': 'boto3-script',
                'project': PROJECT_NAME,
                'upload-time': datetime.now().isoformat()
            }
        }
        
        s3_client.upload_file(file_path, bucket_name, object_key, ExtraArgs=extra_args)
        print(f"✅ File '{file_path}' uploaded to 's3://{bucket_name}/{object_key}'")
        return True
        
    except FileNotFoundError:
        print(f"❌ File '{file_path}' not found.")
        return False
    except ClientError as e:
        print(f"❌ Error uploading file: {e}")
        return False


def upload_string_as_file(bucket_name, content, object_key):
    """
    Upload a string as a file to S3.
    
    Args:
        bucket_name: Target bucket name
        content: String content to upload
        object_key: S3 object key
    
    Returns:
        bool: True if successful
    """
    s3_client = create_s3_client()
    
    try:
        s3_client.put_object(
            Bucket=bucket_name,
            Key=object_key,
            Body=content.encode('utf-8'),
            ContentType='text/plain',
            Metadata={
                'uploaded-by': 'boto3-script',
                'project': PROJECT_NAME
            }
        )
        print(f"✅ Content uploaded to 's3://{bucket_name}/{object_key}'")
        return True
        
    except ClientError as e:
        print(f"❌ Error uploading content: {e}")
        return False


def list_buckets():
    """List all S3 buckets in the account."""
    s3_client = create_s3_client()
    
    try:
        response = s3_client.list_buckets()
        buckets = response.get('Buckets', [])
        
        print("\n📦 S3 Buckets in Account:")
        print("-" * 50)
        
        if not buckets:
            print("No buckets found.")
            return []
        
        for bucket in buckets:
            name = bucket['Name']
            created = bucket['CreationDate'].strftime('%Y-%m-%d %H:%M:%S')
            print(f"  • {name} (Created: {created})")
        
        print(f"\nTotal: {len(buckets)} bucket(s)")
        return buckets
        
    except ClientError as e:
        print(f"❌ Error listing buckets: {e}")
        return []


def list_objects(bucket_name, prefix=''):
    """
    List objects in an S3 bucket.
    
    Args:
        bucket_name: Name of the bucket
        prefix: Filter objects by prefix (optional)
    
    Returns:
        list: List of objects in the bucket
    """
    s3_client = create_s3_client()
    
    try:
        paginator = s3_client.get_paginator('list_objects_v2')
        pages = paginator.paginate(Bucket=bucket_name, Prefix=prefix)
        
        objects = []
        print(f"\n📄 Objects in 's3://{bucket_name}/{prefix}':")
        print("-" * 60)
        
        for page in pages:
            for obj in page.get('Contents', []):
                objects.append(obj)
                size_kb = obj['Size'] / 1024
                modified = obj['LastModified'].strftime('%Y-%m-%d %H:%M:%S')
                print(f"  • {obj['Key']} ({size_kb:.2f} KB, Modified: {modified})")
        
        if not objects:
            print("  No objects found.")
        else:
            print(f"\nTotal: {len(objects)} object(s)")
        
        return objects
        
    except ClientError as e:
        print(f"❌ Error listing objects: {e}")
        return []


def get_bucket_info(bucket_name):
    """
    Get detailed information about a bucket.
    
    Args:
        bucket_name: Name of the bucket
    
    Returns:
        dict: Bucket information
    """
    s3_client = create_s3_client()
    
    info = {'name': bucket_name}
    
    try:
        # Get location
        location = s3_client.get_bucket_location(Bucket=bucket_name)
        info['region'] = location.get('LocationConstraint') or 'us-east-1'
        
        # Get versioning status
        versioning = s3_client.get_bucket_versioning(Bucket=bucket_name)
        info['versioning'] = versioning.get('Status', 'Disabled')
        
        # Get tags
        try:
            tags = s3_client.get_bucket_tagging(Bucket=bucket_name)
            info['tags'] = {tag['Key']: tag['Value'] for tag in tags.get('TagSet', [])}
        except ClientError:
            info['tags'] = {}
        
        print(f"\n🔍 Bucket Information: {bucket_name}")
        print("-" * 50)
        print(f"  Region: {info['region']}")
        print(f"  Versioning: {info['versioning']}")
        print(f"  Tags: {json.dumps(info['tags'], indent=4)}")
        
        return info
        
    except ClientError as e:
        print(f"❌ Error getting bucket info: {e}")
        return info


def delete_object(bucket_name, object_key):
    """
    Delete an object from S3.
    
    Args:
        bucket_name: Name of the bucket
        object_key: Key of the object to delete
    
    Returns:
        bool: True if successful
    """
    s3_client = create_s3_client()
    
    try:
        s3_client.delete_object(Bucket=bucket_name, Key=object_key)
        print(f"✅ Deleted 's3://{bucket_name}/{object_key}'")
        return True
    except ClientError as e:
        print(f"❌ Error deleting object: {e}")
        return False


def main():
    """Main function to demonstrate S3 operations."""
    print("=" * 60)
    print("AWS S3 Operations Demo - Job Portal Project")
    print("=" * 60)
    
    # Generate unique bucket name
    import random
    suffix = ''.join(random.choices('abcdefghijklmnopqrstuvwxyz0123456789', k=8))
    bucket_name = f"{PROJECT_NAME}-{ENVIRONMENT}-files-{suffix}"
    
    print(f"\n🚀 Starting S3 operations demo...")
    print(f"   Bucket name: {bucket_name}")
    print(f"   Region: {REGION}")
    
    # 1. List existing buckets
    print("\n" + "=" * 60)
    print("STEP 1: List Existing Buckets")
    print("=" * 60)
    list_buckets()
    
    # 2. Create a new bucket
    print("\n" + "=" * 60)
    print("STEP 2: Create New Bucket")
    print("=" * 60)
    if create_bucket(bucket_name):
        
        # 3. Upload sample files
        print("\n" + "=" * 60)
        print("STEP 3: Upload Sample Files")
        print("=" * 60)
        
        # Create sample resume content
        sample_resume = """
        John Doe
        Software Engineer
        
        Experience:
        - 5 years of cloud computing experience
        - AWS Certified Solutions Architect
        - Python, Java, JavaScript
        
        Education:
        - BS Computer Science, University XYZ
        """
        
        # Upload as resume
        upload_string_as_file(bucket_name, sample_resume, "resumes/john_doe_resume.txt")
        
        # Upload company logo placeholder
        logo_content = "This is a placeholder for company logo"
        upload_string_as_file(bucket_name, logo_content, "logos/company_logo.txt")
        
        # 4. List uploaded objects
        print("\n" + "=" * 60)
        print("STEP 4: List Uploaded Objects")
        print("=" * 60)
        list_objects(bucket_name)
        
        # 5. Get bucket info
        print("\n" + "=" * 60)
        print("STEP 5: Get Bucket Information")
        print("=" * 60)
        get_bucket_info(bucket_name)
    
    print("\n" + "=" * 60)
    print("S3 Operations Demo Complete!")
    print("=" * 60)
    print(f"\n💡 Remember to clean up resources when done:")
    print(f"   aws s3 rb s3://{bucket_name} --force")


if __name__ == "__main__":
    main()
