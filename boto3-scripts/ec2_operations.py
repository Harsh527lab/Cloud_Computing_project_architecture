"""
EC2 Operations Script using Boto3
=================================
This script demonstrates EC2 instance management, metadata retrieval,
and listing operations using the AWS SDK for Python (Boto3).

Author: Your Name
Course: Cloud Computing
Date: December 2024

Usage:
    python ec2_operations.py
"""

import boto3
import json
import requests
from botocore.exceptions import ClientError
from datetime import datetime

# Configuration
PROJECT_NAME = "job-portal"
ENVIRONMENT = "dev"
REGION = "us-east-1"


def create_ec2_client():
    """Create and return an EC2 client."""
    return boto3.client('ec2', region_name=REGION)


def create_ec2_resource():
    """Create and return an EC2 resource."""
    return boto3.resource('ec2', region_name=REGION)


def list_running_instances():
    """
    List all running EC2 instances.
    
    Returns:
        list: List of running instance details
    """
    ec2_client = create_ec2_client()
    
    try:
        # Filter for running instances
        response = ec2_client.describe_instances(
            Filters=[
                {'Name': 'instance-state-name', 'Values': ['running']}
            ]
        )
        
        instances = []
        print("\n🖥️  Running EC2 Instances:")
        print("-" * 80)
        
        for reservation in response['Reservations']:
            for instance in reservation['Instances']:
                instance_info = {
                    'instance_id': instance['InstanceId'],
                    'instance_type': instance['InstanceType'],
                    'state': instance['State']['Name'],
                    'launch_time': instance['LaunchTime'].strftime('%Y-%m-%d %H:%M:%S'),
                    'private_ip': instance.get('PrivateIpAddress', 'N/A'),
                    'public_ip': instance.get('PublicIpAddress', 'N/A'),
                    'availability_zone': instance['Placement']['AvailabilityZone'],
                    'vpc_id': instance.get('VpcId', 'N/A'),
                    'subnet_id': instance.get('SubnetId', 'N/A')
                }
                
                # Get instance name from tags
                instance_name = 'N/A'
                for tag in instance.get('Tags', []):
                    if tag['Key'] == 'Name':
                        instance_name = tag['Value']
                        break
                instance_info['name'] = instance_name
                
                instances.append(instance_info)
                
                print(f"  Instance: {instance_info['instance_id']}")
                print(f"    Name: {instance_info['name']}")
                print(f"    Type: {instance_info['instance_type']}")
                print(f"    State: {instance_info['state']}")
                print(f"    Private IP: {instance_info['private_ip']}")
                print(f"    Public IP: {instance_info['public_ip']}")
                print(f"    AZ: {instance_info['availability_zone']}")
                print(f"    VPC: {instance_info['vpc_id']}")
                print(f"    Launched: {instance_info['launch_time']}")
                print("-" * 80)
        
        if not instances:
            print("  No running instances found.")
        else:
            print(f"\nTotal: {len(instances)} running instance(s)")
        
        return instances
        
    except ClientError as e:
        print(f"❌ Error listing instances: {e}")
        return []


def list_all_instances():
    """
    List all EC2 instances regardless of state.
    
    Returns:
        list: List of all instance details
    """
    ec2_client = create_ec2_client()
    
    try:
        response = ec2_client.describe_instances()
        
        instances = []
        print("\n📋 All EC2 Instances:")
        print("-" * 80)
        
        state_emoji = {
            'running': '🟢',
            'stopped': '🔴',
            'pending': '🟡',
            'stopping': '🟠',
            'terminated': '⚫'
        }
        
        for reservation in response['Reservations']:
            for instance in reservation['Instances']:
                state = instance['State']['Name']
                emoji = state_emoji.get(state, '⚪')
                
                instance_info = {
                    'instance_id': instance['InstanceId'],
                    'instance_type': instance['InstanceType'],
                    'state': state
                }
                
                # Get instance name
                instance_name = 'N/A'
                for tag in instance.get('Tags', []):
                    if tag['Key'] == 'Name':
                        instance_name = tag['Value']
                        break
                instance_info['name'] = instance_name
                
                instances.append(instance_info)
                print(f"  {emoji} {instance_info['instance_id']} - {instance_name} ({state})")
        
        if not instances:
            print("  No instances found.")
        
        return instances
        
    except ClientError as e:
        print(f"❌ Error listing instances: {e}")
        return []


def get_instance_details(instance_id):
    """
    Get detailed information about a specific instance.
    
    Args:
        instance_id: EC2 instance ID
    
    Returns:
        dict: Instance details
    """
    ec2_client = create_ec2_client()
    
    try:
        response = ec2_client.describe_instances(InstanceIds=[instance_id])
        
        if not response['Reservations']:
            print(f"❌ Instance '{instance_id}' not found.")
            return None
        
        instance = response['Reservations'][0]['Instances'][0]
        
        details = {
            'instance_id': instance['InstanceId'],
            'instance_type': instance['InstanceType'],
            'state': instance['State']['Name'],
            'launch_time': instance['LaunchTime'].isoformat(),
            'private_ip': instance.get('PrivateIpAddress'),
            'public_ip': instance.get('PublicIpAddress'),
            'private_dns': instance.get('PrivateDnsName'),
            'public_dns': instance.get('PublicDnsName'),
            'vpc_id': instance.get('VpcId'),
            'subnet_id': instance.get('SubnetId'),
            'availability_zone': instance['Placement']['AvailabilityZone'],
            'security_groups': [sg['GroupName'] for sg in instance.get('SecurityGroups', [])],
            'ami_id': instance['ImageId'],
            'key_name': instance.get('KeyName'),
            'architecture': instance['Architecture'],
            'root_device_type': instance['RootDeviceType'],
            'tags': {tag['Key']: tag['Value'] for tag in instance.get('Tags', [])}
        }
        
        print(f"\n🔍 Instance Details: {instance_id}")
        print("-" * 60)
        print(json.dumps(details, indent=2, default=str))
        
        return details
        
    except ClientError as e:
        print(f"❌ Error getting instance details: {e}")
        return None


def get_ec2_metadata():
    """
    Retrieve EC2 instance metadata (only works when running on EC2).
    
    Returns:
        dict: Metadata information
    """
    metadata_base_url = "http://169.254.169.254/latest/meta-data/"
    token_url = "http://169.254.169.254/latest/api/token"
    
    try:
        # Get IMDSv2 token
        token_response = requests.put(
            token_url,
            headers={"X-aws-ec2-metadata-token-ttl-seconds": "21600"},
            timeout=2
        )
        token = token_response.text
        headers = {"X-aws-ec2-metadata-token": token}
        
        # Metadata endpoints to retrieve
        endpoints = [
            'instance-id',
            'instance-type',
            'ami-id',
            'hostname',
            'local-hostname',
            'local-ipv4',
            'public-ipv4',
            'public-hostname',
            'placement/availability-zone',
            'placement/region',
            'security-groups',
            'mac'
        ]
        
        metadata = {}
        print("\n🏷️  EC2 Instance Metadata:")
        print("-" * 60)
        
        for endpoint in endpoints:
            try:
                response = requests.get(
                    f"{metadata_base_url}{endpoint}",
                    headers=headers,
                    timeout=2
                )
                if response.status_code == 200:
                    metadata[endpoint] = response.text
                    print(f"  {endpoint}: {response.text}")
            except Exception:
                pass
        
        return metadata
        
    except requests.exceptions.RequestException:
        print("ℹ️  EC2 metadata service not available.")
        print("   (This is normal when running outside of EC2)")
        
        # Return mock data for demonstration
        mock_metadata = {
            'instance-id': 'i-0123456789abcdef0',
            'instance-type': 't2.micro',
            'ami-id': 'ami-0123456789abcdef0',
            'local-ipv4': '10.0.1.100',
            'availability-zone': 'us-east-1a',
            'region': 'us-east-1'
        }
        
        print("\n📝 Mock Metadata (for demonstration):")
        print("-" * 60)
        for key, value in mock_metadata.items():
            print(f"  {key}: {value}")
        
        return mock_metadata


def filter_instances_by_tag(tag_key, tag_value):
    """
    Filter instances by tag.
    
    Args:
        tag_key: Tag key to filter by
        tag_value: Tag value to match
    
    Returns:
        list: Matching instances
    """
    ec2_client = create_ec2_client()
    
    try:
        response = ec2_client.describe_instances(
            Filters=[
                {'Name': f'tag:{tag_key}', 'Values': [tag_value]}
            ]
        )
        
        instances = []
        print(f"\n🏷️  Instances with tag {tag_key}={tag_value}:")
        print("-" * 60)
        
        for reservation in response['Reservations']:
            for instance in reservation['Instances']:
                instance_id = instance['InstanceId']
                state = instance['State']['Name']
                instances.append({'id': instance_id, 'state': state})
                print(f"  • {instance_id} ({state})")
        
        if not instances:
            print("  No matching instances found.")
        
        return instances
        
    except ClientError as e:
        print(f"❌ Error filtering instances: {e}")
        return []


def get_instance_status(instance_id):
    """
    Get the status checks for an instance.
    
    Args:
        instance_id: EC2 instance ID
    
    Returns:
        dict: Status information
    """
    ec2_client = create_ec2_client()
    
    try:
        response = ec2_client.describe_instance_status(
            InstanceIds=[instance_id]
        )
        
        if not response['InstanceStatuses']:
            print(f"ℹ️  No status available for '{instance_id}'")
            print("   (Instance may be stopped or status not yet available)")
            return None
        
        status = response['InstanceStatuses'][0]
        
        status_info = {
            'instance_id': status['InstanceId'],
            'instance_state': status['InstanceState']['Name'],
            'system_status': status['SystemStatus']['Status'],
            'instance_status': status['InstanceStatus']['Status'],
            'availability_zone': status['AvailabilityZone']
        }
        
        print(f"\n✅ Instance Status: {instance_id}")
        print("-" * 60)
        print(f"  State: {status_info['instance_state']}")
        print(f"  System Status: {status_info['system_status']}")
        print(f"  Instance Status: {status_info['instance_status']}")
        print(f"  AZ: {status_info['availability_zone']}")
        
        return status_info
        
    except ClientError as e:
        print(f"❌ Error getting status: {e}")
        return None


def main():
    """Main function to demonstrate EC2 operations."""
    print("=" * 60)
    print("AWS EC2 Operations Demo - Job Portal Project")
    print("=" * 60)
    
    print(f"\n🚀 Starting EC2 operations demo...")
    print(f"   Region: {REGION}")
    print(f"   Project: {PROJECT_NAME}")
    
    # 1. List all instances
    print("\n" + "=" * 60)
    print("STEP 1: List All EC2 Instances")
    print("=" * 60)
    all_instances = list_all_instances()
    
    # 2. List running instances
    print("\n" + "=" * 60)
    print("STEP 2: List Running EC2 Instances")
    print("=" * 60)
    running_instances = list_running_instances()
    
    # 3. Get EC2 metadata (if running on EC2)
    print("\n" + "=" * 60)
    print("STEP 3: Retrieve EC2 Metadata")
    print("=" * 60)
    metadata = get_ec2_metadata()
    
    # 4. Filter instances by project tag
    print("\n" + "=" * 60)
    print("STEP 4: Filter Instances by Project Tag")
    print("=" * 60)
    filter_instances_by_tag('Project', PROJECT_NAME)
    
    # 5. Get details of first running instance (if any)
    if running_instances:
        print("\n" + "=" * 60)
        print("STEP 5: Get Detailed Instance Information")
        print("=" * 60)
        first_instance_id = running_instances[0]['instance_id']
        get_instance_details(first_instance_id)
        get_instance_status(first_instance_id)
    
    print("\n" + "=" * 60)
    print("EC2 Operations Demo Complete!")
    print("=" * 60)


if __name__ == "__main__":
    main()
