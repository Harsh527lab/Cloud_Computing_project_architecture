# =============================================================================
# AWS Job Portal Infrastructure - Terraform Outputs
# =============================================================================

# -----------------------------------------------------------------------------
# VPC Outputs
# -----------------------------------------------------------------------------
output "vpc_id" {
  description = "The ID of the VPC"
  value       = module.vpc.vpc_id
}

output "public_subnet_ids" {
  description = "List of public subnet IDs"
  value       = module.vpc.public_subnet_ids
}

output "private_subnet_ids" {
  description = "List of private subnet IDs"
  value       = module.vpc.private_subnet_ids
}

# -----------------------------------------------------------------------------
# Security Group Outputs
# -----------------------------------------------------------------------------
output "alb_security_group_id" {
  description = "Security group ID for the ALB"
  value       = module.security_groups.alb_sg_id
}

output "ec2_security_group_id" {
  description = "Security group ID for EC2 instances"
  value       = module.security_groups.ec2_sg_id
}

output "rds_security_group_id" {
  description = "Security group ID for RDS"
  value       = module.security_groups.rds_sg_id
}

# -----------------------------------------------------------------------------
# S3 Outputs
# -----------------------------------------------------------------------------
output "s3_bucket_name" {
  description = "Name of the S3 bucket"
  value       = aws_s3_bucket.app_bucket.bucket
}

output "s3_bucket_arn" {
  description = "ARN of the S3 bucket"
  value       = aws_s3_bucket.app_bucket.arn
}

# -----------------------------------------------------------------------------
# Export for CloudFormation
# -----------------------------------------------------------------------------
output "cloudformation_parameters" {
  description = "Parameters to pass to CloudFormation stacks"
  value = {
    vpc_id              = module.vpc.vpc_id
    public_subnet_ids   = join(",", module.vpc.public_subnet_ids)
    private_subnet_ids  = join(",", module.vpc.private_subnet_ids)
    alb_sg_id           = module.security_groups.alb_sg_id
    ec2_sg_id           = module.security_groups.ec2_sg_id
    rds_sg_id           = module.security_groups.rds_sg_id
    s3_bucket_name      = aws_s3_bucket.app_bucket.bucket
  }
}
