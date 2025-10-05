# IntelliClaim AWS Infrastructure Configuration
# Generated for AWS Account: 690353060130

# Basic Configuration
aws_region = "us-east-1"
environment = "dev"
project_name = "intelliclaim"

# Networking Configuration
vpc_cidr = "10.0.0.0/16"
availability_zones = 2

# Database Configuration
db_instance_class = "db.t3.micro"  # Free tier eligible
db_allocated_storage = 20
db_max_allocated_storage = 100
db_password = "IntelliClaim2024!"  # Change this in production!

# ECS Configuration
ecs_cpu = 512
ecs_memory = 1024
ecs_desired_count = 1

# Domain Configuration (optional)
domain_name = ""  # Leave empty for CloudFront domain
certificate_arn = ""  # Not needed without custom domain

# Security Configuration
allowed_cidr_blocks = ["0.0.0.0/0"]

# Monitoring Configuration
enable_detailed_monitoring = true

# Cost Optimization
enable_spot_instances = false  # Set to true for cost savings

# Backup Configuration
backup_retention_period = 7

# GitHub Configuration (update with your repository)
github_repository = "your-username/intelliclaim-project"
github_branch = "main"
github_connection_arn = ""  # Set after creating GitHub connection

