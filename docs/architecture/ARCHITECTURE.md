# Architecture Design Document

## Job Application Portal - AWS Cloud Architecture

### Overview

This document describes the architecture of a scalable Job Application Portal deployed on AWS. The architecture follows cloud best practices including high availability, security, and infrastructure as code principles.

### Architecture Diagram

```
                                    ┌─────────────────────────────────────────────────────────────────┐
                                    │                           AWS CLOUD                              │
                                    │                                                                  │
    ┌──────────┐                    │  ┌───────────────────────────────────────────────────────────┐  │
    │          │                    │  │                         VPC (10.0.0.0/16)                  │  │
    │  Users   │                    │  │                                                            │  │
    │          │                    │  │  ┌─────────────────────┐    ┌─────────────────────────┐   │  │
    └────┬─────┘                    │  │  │   Public Subnet     │    │    Private Subnet        │   │  │
         │                          │  │  │   (10.0.1.0/24)     │    │    (10.0.10.0/24)        │   │  │
         │                          │  │  │                     │    │                          │   │  │
         ▼                          │  │  │  ┌──────────────┐   │    │   ┌──────────────────┐   │   │  │
    ┌──────────┐                    │  │  │  │     ALB      │   │    │   │       RDS        │   │   │  │
    │ Internet │───────────────────────│──│  │   (HTTP/S)   │   │    │   │     (MySQL)      │   │   │  │
    │ Gateway  │                    │  │  │  └──────┬───────┘   │    │   │                  │   │   │  │
    └──────────┘                    │  │  │         │           │    │   └────────▲─────────┘   │   │  │
                                    │  │  │         ▼           │    │            │             │   │  │
                                    │  │  │  ┌──────────────┐   │    │            │             │   │  │
                                    │  │  │  │  EC2 (ASG)   │───┼────┼────────────┘             │   │  │
                                    │  │  │  │  Web Server  │   │    │                          │   │  │
                                    │  │  │  │  (Flask)     │   │    │                          │   │  │
                                    │  │  │  └──────┬───────┘   │    │                          │   │  │
                                    │  │  │         │           │    │                          │   │  │
                                    │  │  └─────────┼───────────┘    └──────────────────────────┘   │  │
                                    │  │            │                                               │  │
                                    │  └────────────┼───────────────────────────────────────────────┘  │
                                    │               │                                                  │
                                    │               ▼                                                  │
                                    │  ┌─────────────────────────┐     ┌─────────────────────────┐     │
                                    │  │          S3             │     │       CloudWatch        │     │
                                    │  │   (Resumes/Logos)       │────▶│        Logs             │     │
                                    │  │                         │     │                         │     │
                                    │  └───────────┬─────────────┘     └─────────────────────────┘     │
                                    │              │                              ▲                    │
                                    │              │ S3 Event                     │                    │
                                    │              ▼                              │                    │
                                    │  ┌─────────────────────────┐                │                    │
                                    │  │        Lambda           │────────────────┘                    │
                                    │  │   (Upload Logger)       │                                     │
                                    │  │                         │                                     │
                                    │  └─────────────────────────┘                                     │
                                    │                                                                  │
                                    └──────────────────────────────────────────────────────────────────┘
```

### Component Details

#### 1. Networking (VPC)

| Component | Configuration |
|-----------|---------------|
| VPC CIDR | 10.0.0.0/16 |
| Public Subnets | 10.0.1.0/24, 10.0.2.0/24 |
| Private Subnets | 10.0.10.0/24, 10.0.20.0/24 |
| Availability Zones | us-east-1a, us-east-1b |
| Internet Gateway | For public internet access |
| NAT Gateway | For private subnet outbound access |

#### 2. Compute (EC2)

| Component | Configuration |
|-----------|---------------|
| Instance Type | t2.micro (Free Tier eligible) |
| AMI | Amazon Linux 2 |
| Auto Scaling | Min: 1, Max: 3, Desired: 2 |
| Scaling Policy | Target CPU 70% |
| Placement | Public subnets (behind ALB) |

#### 3. Load Balancing (ALB)

| Component | Configuration |
|-----------|---------------|
| Type | Application Load Balancer |
| Scheme | Internet-facing |
| Listeners | HTTP (Port 80) |
| Health Check | /health endpoint |
| Target Type | Instance |

#### 4. Database (RDS)

| Component | Configuration |
|-----------|---------------|
| Engine | MySQL 8.0 |
| Instance Class | db.t3.micro |
| Storage | 20 GB GP2 |
| Multi-AZ | No (for dev environment) |
| Placement | Private subnet |
| Encryption | Enabled |

#### 5. Storage (S3)

| Component | Configuration |
|-----------|---------------|
| Bucket Purpose | Resumes, logos, static files |
| Versioning | Enabled |
| Encryption | AES-256 |
| Access | Private (via IAM) |

#### 6. Serverless (Lambda)

| Component | Configuration |
|-----------|---------------|
| Runtime | Python 3.11 |
| Memory | 128 MB |
| Timeout | 30 seconds |
| Trigger | S3 ObjectCreated events |
| Output | CloudWatch Logs |

### Security Architecture

#### Security Groups

```
┌─────────────────────────────────────────────────────────────────┐
│                    Security Group Rules                          │
├─────────────────┬───────────────────────────────────────────────┤
│ ALB SG          │ Inbound: 80, 443 from 0.0.0.0/0              │
│                 │ Outbound: All traffic                         │
├─────────────────┼───────────────────────────────────────────────┤
│ EC2 SG          │ Inbound: 80 from ALB SG, 22 from Admin IP    │
│                 │ Outbound: All traffic                         │
├─────────────────┼───────────────────────────────────────────────┤
│ RDS SG          │ Inbound: 3306 from EC2 SG only               │
│                 │ Outbound: None required                       │
└─────────────────┴───────────────────────────────────────────────┘
```

### Data Flow

1. **User Request Flow**
   - User → Internet Gateway → ALB → EC2 → RDS
   
2. **File Upload Flow**
   - User uploads file → EC2 → S3 → S3 Event → Lambda → CloudWatch

3. **Scaling Flow**
   - CloudWatch monitors CPU → Triggers ASG → Launch/Terminate EC2

### Infrastructure as Code

| Tool | Purpose |
|------|---------|
| Terraform | VPC, Subnets, Security Groups, S3 |
| CloudFormation | EC2, ALB, RDS, Lambda |

### Cost Optimization

- Use t2.micro instances (Free Tier eligible)
- Single NAT Gateway (acceptable for dev)
- Auto Scaling to match demand
- RDS Single-AZ for development

### Future Improvements

1. Add HTTPS with ACM certificate
2. Implement CloudFront CDN
3. Add API Gateway for REST API
4. Enable RDS Multi-AZ for production
5. Implement CI/CD pipeline
6. Add WAF for security
