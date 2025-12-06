"""
Lambda Operations Script using Boto3
====================================
This script demonstrates Lambda function management and invocation
using the AWS SDK for Python (Boto3).

Author: Your Name
Course: Cloud Computing
Date: December 2024

Usage:
    python lambda_operations.py
"""

import boto3
import json
import base64
from botocore.exceptions import ClientError
from datetime import datetime

# Configuration
PROJECT_NAME = "job-portal"
ENVIRONMENT = "dev"
REGION = "us-east-1"
LAMBDA_FUNCTION_NAME = f"{PROJECT_NAME}-{ENVIRONMENT}-s3-upload-logger"


def create_lambda_client():
    """Create and return a Lambda client."""
    return boto3.client('lambda', region_name=REGION)


def create_logs_client():
    """Create and return a CloudWatch Logs client."""
    return boto3.client('logs', region_name=REGION)


def list_lambda_functions():
    """
    List all Lambda functions in the account.
    
    Returns:
        list: List of Lambda function details
    """
    lambda_client = create_lambda_client()
    
    try:
        paginator = lambda_client.get_paginator('list_functions')
        
        functions = []
        print("\n⚡ Lambda Functions:")
        print("-" * 80)
        
        for page in paginator.paginate():
            for func in page['Functions']:
                func_info = {
                    'name': func['FunctionName'],
                    'runtime': func.get('Runtime', 'N/A'),
                    'memory': func['MemorySize'],
                    'timeout': func['Timeout'],
                    'last_modified': func['LastModified'],
                    'description': func.get('Description', 'No description')
                }
                functions.append(func_info)
                
                print(f"  Function: {func_info['name']}")
                print(f"    Runtime: {func_info['runtime']}")
                print(f"    Memory: {func_info['memory']} MB")
                print(f"    Timeout: {func_info['timeout']} seconds")
                print(f"    Description: {func_info['description'][:50]}...")
                print(f"    Last Modified: {func_info['last_modified']}")
                print("-" * 80)
        
        if not functions:
            print("  No Lambda functions found.")
        else:
            print(f"\nTotal: {len(functions)} function(s)")
        
        return functions
        
    except ClientError as e:
        print(f"❌ Error listing functions: {e}")
        return []


def get_function_details(function_name):
    """
    Get detailed information about a Lambda function.
    
    Args:
        function_name: Name of the Lambda function
    
    Returns:
        dict: Function details
    """
    lambda_client = create_lambda_client()
    
    try:
        response = lambda_client.get_function(FunctionName=function_name)
        
        config = response['Configuration']
        details = {
            'name': config['FunctionName'],
            'arn': config['FunctionArn'],
            'runtime': config.get('Runtime', 'N/A'),
            'role': config['Role'],
            'handler': config['Handler'],
            'memory': config['MemorySize'],
            'timeout': config['Timeout'],
            'description': config.get('Description', ''),
            'last_modified': config['LastModified'],
            'code_size': config['CodeSize'],
            'state': config.get('State', 'Active'),
            'architectures': config.get('Architectures', ['x86_64'])
        }
        
        print(f"\n🔍 Lambda Function Details: {function_name}")
        print("-" * 60)
        print(f"  ARN: {details['arn']}")
        print(f"  Runtime: {details['runtime']}")
        print(f"  Handler: {details['handler']}")
        print(f"  Memory: {details['memory']} MB")
        print(f"  Timeout: {details['timeout']} seconds")
        print(f"  Code Size: {details['code_size'] / 1024:.2f} KB")
        print(f"  State: {details['state']}")
        print(f"  Architecture: {', '.join(details['architectures'])}")
        print(f"  IAM Role: {details['role']}")
        print(f"  Last Modified: {details['last_modified']}")
        
        return details
        
    except ClientError as e:
        if e.response['Error']['Code'] == 'ResourceNotFoundException':
            print(f"❌ Function '{function_name}' not found.")
        else:
            print(f"❌ Error getting function details: {e}")
        return None


def invoke_lambda(function_name, payload=None, invocation_type='RequestResponse'):
    """
    Invoke a Lambda function.
    
    Args:
        function_name: Name of the Lambda function
        payload: Event payload to send (dict)
        invocation_type: 'RequestResponse' (sync) or 'Event' (async)
    
    Returns:
        dict: Invocation response
    """
    lambda_client = create_lambda_client()
    
    if payload is None:
        # Default test payload simulating S3 upload event
        payload = {
            "Records": [
                {
                    "eventTime": datetime.now().isoformat(),
                    "eventName": "ObjectCreated:Put",
                    "s3": {
                        "bucket": {
                            "name": f"{PROJECT_NAME}-{ENVIRONMENT}-files"
                        },
                        "object": {
                            "key": "resumes/test_resume.pdf",
                            "size": 102400
                        }
                    },
                    "requestParameters": {
                        "sourceIPAddress": "192.168.1.100"
                    },
                    "userIdentity": {
                        "principalId": "BOTO3_TEST_USER"
                    }
                }
            ]
        }
    
    try:
        print(f"\n🚀 Invoking Lambda Function: {function_name}")
        print("-" * 60)
        print(f"  Invocation Type: {invocation_type}")
        print(f"  Payload: {json.dumps(payload, indent=2)}")
        
        response = lambda_client.invoke(
            FunctionName=function_name,
            InvocationType=invocation_type,
            Payload=json.dumps(payload)
        )
        
        status_code = response['StatusCode']
        
        result = {
            'status_code': status_code,
            'executed_version': response.get('ExecutedVersion', '$LATEST'),
            'function_error': response.get('FunctionError')
        }
        
        # Read response payload
        if 'Payload' in response:
            payload_response = json.loads(response['Payload'].read())
            result['response'] = payload_response
        
        print(f"\n✅ Lambda Invocation Result:")
        print("-" * 60)
        print(f"  Status Code: {result['status_code']}")
        print(f"  Executed Version: {result['executed_version']}")
        
        if result['function_error']:
            print(f"  ⚠️  Function Error: {result['function_error']}")
        
        if 'response' in result:
            print(f"  Response: {json.dumps(result['response'], indent=2)}")
        
        return result
        
    except ClientError as e:
        if e.response['Error']['Code'] == 'ResourceNotFoundException':
            print(f"❌ Function '{function_name}' not found.")
        else:
            print(f"❌ Error invoking function: {e}")
        return None


def get_function_logs(function_name, limit=10):
    """
    Get recent CloudWatch logs for a Lambda function.
    
    Args:
        function_name: Name of the Lambda function
        limit: Number of log events to retrieve
    
    Returns:
        list: Log events
    """
    logs_client = create_logs_client()
    log_group_name = f"/aws/lambda/{function_name}"
    
    try:
        # Get log streams
        streams_response = logs_client.describe_log_streams(
            logGroupName=log_group_name,
            orderBy='LastEventTime',
            descending=True,
            limit=1
        )
        
        if not streams_response.get('logStreams'):
            print(f"ℹ️  No log streams found for '{function_name}'")
            return []
        
        log_stream_name = streams_response['logStreams'][0]['logStreamName']
        
        # Get log events
        events_response = logs_client.get_log_events(
            logGroupName=log_group_name,
            logStreamName=log_stream_name,
            limit=limit,
            startFromHead=False
        )
        
        events = events_response.get('events', [])
        
        print(f"\n📜 Recent Logs for: {function_name}")
        print(f"   Log Stream: {log_stream_name}")
        print("-" * 80)
        
        for event in events:
            timestamp = datetime.fromtimestamp(event['timestamp'] / 1000)
            message = event['message'].strip()
            print(f"  [{timestamp}] {message}")
        
        if not events:
            print("  No log events found.")
        
        return events
        
    except ClientError as e:
        if e.response['Error']['Code'] == 'ResourceNotFoundException':
            print(f"ℹ️  Log group not found. Function may not have been invoked yet.")
        else:
            print(f"❌ Error getting logs: {e}")
        return []


def get_function_configuration(function_name):
    """
    Get environment variables and configuration for a Lambda function.
    
    Args:
        function_name: Name of the Lambda function
    
    Returns:
        dict: Configuration details
    """
    lambda_client = create_lambda_client()
    
    try:
        response = lambda_client.get_function_configuration(
            FunctionName=function_name
        )
        
        config = {
            'environment': response.get('Environment', {}).get('Variables', {}),
            'vpc_config': response.get('VpcConfig', {}),
            'dead_letter_config': response.get('DeadLetterConfig', {}),
            'tracing_config': response.get('TracingConfig', {}),
            'layers': [layer['Arn'] for layer in response.get('Layers', [])]
        }
        
        print(f"\n⚙️  Function Configuration: {function_name}")
        print("-" * 60)
        
        print("  Environment Variables:")
        if config['environment']:
            for key, value in config['environment'].items():
                print(f"    {key}: {value}")
        else:
            print("    None configured")
        
        print(f"\n  VPC Config: {'Configured' if config['vpc_config'].get('VpcId') else 'Not in VPC'}")
        print(f"  Tracing: {config['tracing_config'].get('Mode', 'PassThrough')}")
        print(f"  Layers: {len(config['layers'])} layer(s)")
        
        return config
        
    except ClientError as e:
        print(f"❌ Error getting configuration: {e}")
        return None


def invoke_lambda_async(function_name, payload=None):
    """
    Invoke a Lambda function asynchronously.
    
    Args:
        function_name: Name of the Lambda function
        payload: Event payload to send
    
    Returns:
        dict: Invocation response
    """
    return invoke_lambda(function_name, payload, invocation_type='Event')


def main():
    """Main function to demonstrate Lambda operations."""
    print("=" * 60)
    print("AWS Lambda Operations Demo - Job Portal Project")
    print("=" * 60)
    
    print(f"\n🚀 Starting Lambda operations demo...")
    print(f"   Region: {REGION}")
    print(f"   Target Function: {LAMBDA_FUNCTION_NAME}")
    
    # 1. List all Lambda functions
    print("\n" + "=" * 60)
    print("STEP 1: List All Lambda Functions")
    print("=" * 60)
    list_lambda_functions()
    
    # 2. Get function details
    print("\n" + "=" * 60)
    print("STEP 2: Get Function Details")
    print("=" * 60)
    details = get_function_details(LAMBDA_FUNCTION_NAME)
    
    if details:
        # 3. Get function configuration
        print("\n" + "=" * 60)
        print("STEP 3: Get Function Configuration")
        print("=" * 60)
        get_function_configuration(LAMBDA_FUNCTION_NAME)
        
        # 4. Invoke Lambda function manually
        print("\n" + "=" * 60)
        print("STEP 4: Invoke Lambda Function (Synchronous)")
        print("=" * 60)
        invoke_lambda(LAMBDA_FUNCTION_NAME)
        
        # 5. Get function logs
        print("\n" + "=" * 60)
        print("STEP 5: Get Recent Function Logs")
        print("=" * 60)
        get_function_logs(LAMBDA_FUNCTION_NAME, limit=20)
    else:
        print(f"\n⚠️  Function '{LAMBDA_FUNCTION_NAME}' not found.")
        print("   Please deploy the Lambda function first using CloudFormation.")
        print("\n   To deploy:")
        print(f"   aws cloudformation create-stack \\")
        print(f"       --stack-name {PROJECT_NAME}-lambda \\")
        print(f"       --template-body file://cloudformation/lambda-stack.yaml \\")
        print(f"       --capabilities CAPABILITY_IAM \\")
        print(f"       --parameters ParameterKey=S3BucketName,ParameterValue=your-bucket-name")
    
    print("\n" + "=" * 60)
    print("Lambda Operations Demo Complete!")
    print("=" * 60)


if __name__ == "__main__":
    main()
