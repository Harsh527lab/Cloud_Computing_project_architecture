# AWS Job Application Portal - Infrastructure as Code

[![AWS](https://img.shields.io/badge/AWS-Cloud-orange?logo=amazon-aws)](https://aws.amazon.com/)
[![Terraform](https://img.shields.io/badge/Terraform-IaC-purple?logo=terraform)](https://www.terraform.io/)
[![Python](https://img.shields.io/badge/Python-3.9+-blue?logo=python)](https://www.python.org/)

## 📋 Project Overview

A scalable, cloud-based Job Application Portal deployed on AWS using Infrastructure as Code (IaC) principles. This project demonstrates the implementation of a multi-tier architecture using Terraform, CloudFormation, and Python Boto3.

### Architecture Highlights

- **Networking**: VPC with public and private subnets across availability zones
- **Compute**: EC2 instances behind an Application Load Balancer with Auto Scaling
- **Database**: Amazon RDS (MySQL) in private subnet
- **Storage**: S3 bucket for resumes, company logos, and static assets
- **Serverless**: Lambda function triggered by S3 uploads, logging to CloudWatch
- **Security**: Security groups with least-privilege access controls

## 🏗️ Architecture Diagram

![Architecture Diagram](docs/architecture/architecture-diagram.png)

## 📁 Project Structure

```
aws-job-portal-infrastructure/
├── terraform/                    # Terraform IaC scripts
│   ├── main.tf                   # Main Terraform configuration
│   ├── variables.tf              # Variable definitions
│   ├── outputs.tf                # Output definitions
│   ├── terraform.tfvars          # Variable values (DO NOT COMMIT)
│   └── modules/
│       ├── vpc/                  # VPC module
│       └── security-groups/      # Security groups module
├── cloudformation/               # CloudFormation templates
│   ├── ec2-stack.yaml            # EC2 and ALB resources
│   ├── rds-stack.yaml            # RDS database resources
│   └── lambda-stack.yaml         # Lambda function resources
├── lambda/                       # Lambda function code
│   └── s3_upload_logger.py       # S3 event logging function
├── boto3-scripts/                # Python Boto3 scripts
│   ├── s3_operations.py          # S3 bucket and upload operations
│   ├── ec2_operations.py         # EC2 metadata and listing
│   └── lambda_operations.py      # Lambda invocation
├── web-app/                      # Web application code
│   ├── app.py                    # Flask application
│   ├── templates/                # HTML templates
│   └── static/                   # CSS, JS, images
├── docs/                         # Documentation
│   ├── architecture/             # Architecture diagrams
│   └── screenshots/              # Deployment screenshots
├── scripts/                      # Utility scripts
│   └── deploy.sh                 # Deployment automation
├── .gitignore                    # Git ignore rules
└── README.md                     # This file
```

## 🚀 Prerequisites

- AWS Account with appropriate permissions
- AWS CLI configured with credentials
- Terraform >= 1.0.0
- Python >= 3.9
- Git

## ⚙️ Setup Instructions

### 1. Clone the Repository

```bash
git clone https://github.com/YOUR_USERNAME/aws-job-portal-infrastructure.git
cd aws-job-portal-infrastructure
```

### 2. Configure AWS Credentials

```bash
aws configure
# Enter your AWS Access Key ID
# Enter your AWS Secret Access Key
# Enter default region (e.g., us-east-1)
# Enter output format (json)
```

### 3. Deploy Infrastructure with Terraform

```bash
cd terraform
terraform init
terraform plan
terraform apply
```

### 4. Deploy Resources with CloudFormation

```bash
# Deploy EC2 Stack
aws cloudformation create-stack --stack-name job-portal-ec2 \
    --template-body file://cloudformation/ec2-stack.yaml \
    --capabilities CAPABILITY_IAM

# Deploy RDS Stack
aws cloudformation create-stack --stack-name job-portal-rds \
    --template-body file://cloudformation/rds-stack.yaml

# Deploy Lambda Stack
aws cloudformation create-stack --stack-name job-portal-lambda \
    --template-body file://cloudformation/lambda-stack.yaml \
    --capabilities CAPABILITY_IAM
```

### 5. Run Boto3 Scripts

```bash
cd boto3-scripts
pip install boto3
python s3_operations.py
python ec2_operations.py
python lambda_operations.py
```

## 🔧 AWS Services Used

| Service | Purpose |
|---------|---------|
| VPC | Network isolation with public/private subnets |
| EC2 | Web application hosting |
| ALB | Load balancing and traffic distribution |
| Auto Scaling | Dynamic scaling based on demand |
| RDS (MySQL) | Relational database for job data |
| S3 | Object storage for files |
| Lambda | Serverless compute for S3 event logging |
| CloudWatch | Monitoring and logging |
| IAM | Access management |

## 📊 AWS Interaction Methods

This project demonstrates three methods of AWS interaction:

1. **AWS Management Console** - Visual verification of deployments
2. **AWS CLI** - Command-line resource management
3. **Python Boto3** - Programmatic AWS operations

## 🧪 Testing

### Verify Lambda Function

```bash
# Upload a test file to S3
aws s3 cp test-resume.pdf s3://job-portal-bucket/resumes/

# Check CloudWatch Logs
aws logs tail /aws/lambda/s3-upload-logger --follow
```

### Verify Web Application

```bash
# Get ALB DNS name
aws elbv2 describe-load-balancers --query 'LoadBalancers[0].DNSName'
# Access the application via browser
```

## 📝 Documentation

- [Architecture Design](docs/architecture/ARCHITECTURE.md)
- [Deployment Guide](docs/DEPLOYMENT.md)
- [Troubleshooting](docs/TROUBLESHOOTING.md)

## 🔒 Security Considerations

- RDS instance placed in private subnet (no public access)
- Security groups follow least-privilege principle
- S3 bucket has appropriate access policies
- Sensitive data stored in AWS Secrets Manager
- IAM roles with minimal required permissions

## 🚧 Future Improvements

- [ ] Implement CI/CD pipeline with GitHub Actions
- [ ] Add API Gateway for RESTful API
- [ ] Implement Step Functions for workflow automation
- [ ] Add CloudFront CDN for static assets
- [ ] Implement multi-region disaster recovery

## 👤 Author

**Your Name**
- Course: Cloud Computing
- Institution: Your University
- Date: December 2024

## 📄 License

This project is for educational purposes as part of a cloud computing course.
