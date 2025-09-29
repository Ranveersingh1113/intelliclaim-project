# RDS Aurora PostgreSQL with pgvector Configuration

# DB Subnet Group
resource "aws_db_subnet_group" "main" {
  name       = "${local.name}-db-subnet-group"
  subnet_ids = aws_subnet.private[*].id

  tags = merge(local.common_tags, {
    Name = "${local.name}-db-subnet-group"
  })
}

# Security Group for RDS
resource "aws_security_group" "rds" {
  name_prefix = "${local.name}-rds-"
  vpc_id      = aws_vpc.main.id

  ingress {
    from_port       = 5432
    to_port         = 5432
    protocol        = "tcp"
    security_groups = [aws_security_group.ecs_tasks.id]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = merge(local.common_tags, {
    Name = "${local.name}-rds-sg"
  })

  lifecycle {
    create_before_destroy = true
  }
}

# RDS Parameter Group for pgvector
resource "aws_db_parameter_group" "main" {
  family = "aurora-postgresql15"
  name   = "${local.name}-pg-params"

  parameter {
    name  = "shared_preload_libraries"
    value = "vector"
  }

  tags = merge(local.common_tags, {
    Name = "${local.name}-db-parameter-group"
  })
}

# RDS Cluster
resource "aws_rds_cluster" "main" {
  cluster_identifier      = "${local.name}-aurora-cluster"
  engine                  = "aurora-postgresql"
  engine_mode             = "provisioned"
  engine_version          = "15.4"
  database_name           = "intelliclaim"
  master_username         = "postgres"
  master_password         = var.db_password
  backup_retention_period = var.backup_retention_period
  preferred_backup_window = "03:00-04:00"
  preferred_maintenance_window = "sun:04:00-sun:05:00"
  skip_final_snapshot    = var.environment != "prod"
  final_snapshot_identifier = var.environment == "prod" ? "${local.name}-final-snapshot-${formatdate("YYYY-MM-DD-hhmm", timestamp())}" : null
  
  db_subnet_group_name   = aws_db_subnet_group.main.name
  vpc_security_group_ids = [aws_security_group.rds.id]
  db_cluster_parameter_group_name = aws_db_parameter_group.main.name
  
  storage_encrypted = true
  kms_key_id        = aws_kms_key.rds.arn

  tags = merge(local.common_tags, {
    Name = "${local.name}-aurora-cluster"
  })
}

# RDS Cluster Instance
resource "aws_rds_cluster_instance" "main" {
  count              = 1  # Single instance for cost optimization
  identifier         = "${local.name}-aurora-instance-${count.index + 1}"
  cluster_identifier = aws_rds_cluster.main.id
  instance_class     = var.db_instance_class
  engine             = aws_rds_cluster.main.engine
  engine_version     = aws_rds_cluster.main.engine_version

  performance_insights_enabled = var.enable_detailed_monitoring
  monitoring_interval          = var.enable_detailed_monitoring ? 60 : 0
  monitoring_role_arn          = var.enable_detailed_monitoring ? aws_iam_role.rds_monitoring[0].arn : null

  tags = merge(local.common_tags, {
    Name = "${local.name}-aurora-instance-${count.index + 1}"
  })
}

# KMS Key for RDS encryption
resource "aws_kms_key" "rds" {
  description             = "KMS key for RDS encryption"
  deletion_window_in_days = 7

  tags = merge(local.common_tags, {
    Name = "${local.name}-rds-kms"
  })
}

resource "aws_kms_alias" "rds" {
  name          = "alias/${local.name}-rds"
  target_key_id = aws_kms_key.rds.key_id
}

# IAM Role for RDS Enhanced Monitoring
resource "aws_iam_role" "rds_monitoring" {
  count = var.enable_detailed_monitoring ? 1 : 0

  name = "${local.name}-rds-monitoring-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "monitoring.rds.amazonaws.com"
        }
      }
    ]
  })

  tags = local.common_tags
}

resource "aws_iam_role_policy_attachment" "rds_monitoring" {
  count = var.enable_detailed_monitoring ? 1 : 0

  role       = aws_iam_role.rds_monitoring[0].name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AmazonRDSEnhancedMonitoringRole"
}

# Secrets Manager for database credentials
resource "aws_secretsmanager_secret" "db_credentials" {
  name                    = "${local.name}/database/credentials"
  description             = "Database credentials for IntelliClaim"
  recovery_window_in_days = 7

  tags = local.common_tags
}

resource "aws_secretsmanager_secret_version" "db_credentials" {
  secret_id = aws_secretsmanager_secret.db_credentials.id
  secret_string = jsonencode({
    username = aws_rds_cluster.main.master_username
    password = aws_rds_cluster.main.master_password
    host     = aws_rds_cluster.main.endpoint
    port     = aws_rds_cluster.main.port
    database = aws_rds_cluster.main.database_name
  })
}

# DB Password variable (should be set via environment or secrets)
variable "db_password" {
  description = "Master password for the database"
  type        = string
  sensitive   = true
  default     = "TempPassword123!"  # Change this in production!
}
