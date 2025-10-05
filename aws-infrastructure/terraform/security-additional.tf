# Additional Security Configurations

# AWS Config for compliance monitoring
resource "aws_config_configuration_recorder" "main" {
  count = var.environment == "prod" ? 1 : 0

  name     = "${local.name}-config-recorder"
  role_arn = aws_iam_role.config_role[0].arn

  recording_group {
    all_supported                 = true
    include_global_resource_types = true
  }

  depends_on = [aws_config_delivery_channel.main]
}

resource "aws_config_delivery_channel" "main" {
  count = var.environment == "prod" ? 1 : 0

  name           = "${local.name}-config-delivery"
  s3_bucket_name = aws_s3_bucket.config[0].bucket
  s3_key_prefix  = "config"
  s3_kms_key_arn = aws_kms_key.config[0].arn
}

# KMS Key for Config
resource "aws_kms_key" "config" {
  count = var.environment == "prod" ? 1 : 0

  description             = "KMS key for AWS Config"
  deletion_window_in_days = 7

  tags = merge(local.common_tags, {
    Name = "${local.name}-config-kms"
  })
}

resource "aws_kms_alias" "config" {
  count = var.environment == "prod" ? 1 : 0

  name          = "alias/${local.name}-config"
  target_key_id = aws_kms_key.config[0].key_id
}

# S3 bucket for Config logs
resource "aws_s3_bucket" "config" {
  count = var.environment == "prod" ? 1 : 0

  bucket = "${local.name}-config-${random_string.bucket_suffix.result}"

  tags = local.common_tags
}

resource "aws_s3_bucket_versioning" "config" {
  count = var.environment == "prod" ? 1 : 0

  bucket = aws_s3_bucket.config[0].id
  versioning_configuration {
    status = "Enabled"
  }
}

resource "aws_s3_bucket_server_side_encryption_configuration" "config" {
  count = var.environment == "prod" ? 1 : 0

  bucket = aws_s3_bucket.config[0].id

  rule {
    apply_server_side_encryption_by_default {
      kms_master_key_id = aws_kms_key.config[0].arn
      sse_algorithm     = "aws:kms"
    }
    bucket_key_enabled = true
  }
}

resource "aws_s3_bucket_public_access_block" "config" {
  count = var.environment == "prod" ? 1 : 0

  bucket = aws_s3_bucket.config[0].id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

# IAM Role for AWS Config
resource "aws_iam_role" "config_role" {
  count = var.environment == "prod" ? 1 : 0

  name = "${local.name}-config-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "config.amazonaws.com"
        }
      }
    ]
  })

  tags = local.common_tags
}

resource "aws_iam_role_policy_attachment" "config_role_policy" {
  count = var.environment == "prod" ? 1 : 0

  role       = aws_iam_role.config_role[0].name
  policy_arn = "arn:aws:iam::aws:policy/service-role/ConfigRole"
}

# Security Hub (optional - for advanced threat detection)
resource "aws_securityhub_account" "main" {
  count = var.environment == "prod" ? 1 : 0

  enable_default_standards = true

  tags = local.common_tags
}

# GuardDuty Detector
resource "aws_guardduty_detector" "main" {
  count = var.environment == "prod" ? 1 : 0

  enable = true

  datasources {
    s3_logs {
      enable = true
    }
    kubernetes {
      audit_logs {
        enable = true
      }
    }
    malware_protection {
      scan_ec2_instance_with_findings {
        ebs_volumes {
          enable = true
        }
      }
    }
  }

  tags = local.common_tags
}

# CloudTrail for audit logging
resource "aws_cloudtrail" "main" {
  count = var.environment == "prod" ? 1 : 0

  name                          = "${local.name}-cloudtrail"
  s3_bucket_name                = aws_s3_bucket.cloudtrail[0].bucket
  include_global_service_events = true
  is_multi_region_trail         = true
  enable_logging                = true

  event_selector {
    read_write_type           = "All"
    include_management_events = true
    data_resource {
      type   = "AWS::S3::Object"
      values = ["arn:aws:s3:::*/*"]
    }
  }

  event_selector {
    read_write_type           = "All"
    include_management_events = true
    data_resource {
      type   = "AWS::RDS::Database"
      values = ["arn:aws:rds:::*"]
    }
  }

  tags = local.common_tags
}

# S3 bucket for CloudTrail
resource "aws_s3_bucket" "cloudtrail" {
  count = var.environment == "prod" ? 1 : 0

  bucket = "${local.name}-cloudtrail-${random_string.bucket_suffix.result}"

  tags = local.common_tags
}

resource "aws_s3_bucket_versioning" "cloudtrail" {
  count = var.environment == "prod" ? 1 : 0

  bucket = aws_s3_bucket.cloudtrail[0].id
  versioning_configuration {
    status = "Enabled"
  }
}

resource "aws_s3_bucket_server_side_encryption_configuration" "cloudtrail" {
  count = var.environment == "prod" ? 1 : 0

  bucket = aws_s3_bucket.cloudtrail[0].id

  rule {
    apply_server_side_encryption_by_default {
      kms_master_key_id = aws_kms_key.cloudtrail[0].arn
      sse_algorithm     = "aws:kms"
    }
    bucket_key_enabled = true
  }
}

resource "aws_s3_bucket_public_access_block" "cloudtrail" {
  count = var.environment == "prod" ? 1 : 0

  bucket = aws_s3_bucket.cloudtrail[0].id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

# KMS Key for CloudTrail
resource "aws_kms_key" "cloudtrail" {
  count = var.environment == "prod" ? 1 : 0

  description             = "KMS key for CloudTrail"
  deletion_window_in_days = 7

  tags = merge(local.common_tags, {
    Name = "${local.name}-cloudtrail-kms"
  })
}

resource "aws_kms_alias" "cloudtrail" {
  count = var.environment == "prod" ? 1 : 0

  name          = "alias/${local.name}-cloudtrail"
  target_key_id = aws_kms_key.cloudtrail[0].key_id
}

# S3 bucket policy for CloudTrail
resource "aws_s3_bucket_policy" "cloudtrail" {
  count = var.environment == "prod" ? 1 : 0

  bucket = aws_s3_bucket.cloudtrail[0].id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Sid    = "AWSCloudTrailAclCheck"
        Effect = "Allow"
        Principal = {
          Service = "cloudtrail.amazonaws.com"
        }
        Action   = "s3:GetBucketAcl"
        Resource = aws_s3_bucket.cloudtrail[0].arn
        Condition = {
          StringEquals = {
            "AWS:SourceArn" = "arn:aws:cloudtrail:${var.aws_region}:${data.aws_caller_identity.current.account_id}:trail/${local.name}-cloudtrail"
          }
        }
      },
      {
        Sid    = "AWSCloudTrailWrite"
        Effect = "Allow"
        Principal = {
          Service = "cloudtrail.amazonaws.com"
        }
        Action   = "s3:PutObject"
        Resource = "${aws_s3_bucket.cloudtrail[0].arn}/*"
        Condition = {
          StringEquals = {
            "AWS:SourceArn" = "arn:aws:cloudtrail:${var.aws_region}:${data.aws_caller_identity.current.account_id}:trail/${local.name}-cloudtrail"
            "s3:x-amz-acl"  = "bucket-owner-full-control"
          }
        }
      }
    ]
  })
}

# AWS Systems Manager Parameter Store for sensitive configuration
resource "aws_ssm_parameter" "app_config" {
  name = "/${local.name}/app/config"
  type = "String"
  value = jsonencode({
    environment = var.environment
    region      = var.aws_region
    version     = "2.0.0"
  })

  tags = local.common_tags
}

# AWS Systems Manager Parameter Store for database connection
resource "aws_ssm_parameter" "db_config" {
  name = "/${local.name}/database/config"
  type = "SecureString"
  value = jsonencode({
    host     = aws_rds_cluster.main.endpoint
    port     = aws_rds_cluster.main.port
    database = aws_rds_cluster.main.database_name
    username = aws_rds_cluster.main.master_username
  })

  tags = local.common_tags
}

# AWS Backup Vault
resource "aws_backup_vault" "main" {
  count = var.environment == "prod" ? 1 : 0

  name        = "${local.name}-backup-vault"
  kms_key_arn = aws_kms_key.backup[0].arn

  tags = local.common_tags
}

# KMS Key for Backup
resource "aws_kms_key" "backup" {
  count = var.environment == "prod" ? 1 : 0

  description             = "KMS key for AWS Backup"
  deletion_window_in_days = 7

  tags = merge(local.common_tags, {
    Name = "${local.name}-backup-kms"
  })
}

resource "aws_kms_alias" "backup" {
  count = var.environment == "prod" ? 1 : 0

  name          = "alias/${local.name}-backup"
  target_key_id = aws_kms_key.backup[0].key_id
}

# AWS Backup Plan
resource "aws_backup_plan" "main" {
  count = var.environment == "prod" ? 1 : 0

  name = "${local.name}-backup-plan"

  rule {
    rule_name         = "${local.name}-backup-rule"
    target_vault_name = aws_backup_vault.main[0].name
    schedule          = "cron(0 2 * * ? *)" # Daily at 2 AM

    lifecycle {
      cold_storage_after = 30
      delete_after       = 90
    }

    recovery_point_tags = local.common_tags
  }

  tags = local.common_tags
}

# AWS Backup Selection
resource "aws_backup_selection" "main" {
  count = var.environment == "prod" ? 1 : 0

  iam_role_arn = aws_iam_role.backup_role[0].arn
  name         = "${local.name}-backup-selection"
  plan_id      = aws_backup_plan.main[0].id

  resources = [
    aws_rds_cluster.main.arn,
    aws_s3_bucket.main.arn
  ]

  tags = local.common_tags
}

# IAM Role for AWS Backup
resource "aws_iam_role" "backup_role" {
  count = var.environment == "prod" ? 1 : 0

  name = "${local.name}-backup-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "backup.amazonaws.com"
        }
      }
    ]
  })

  tags = local.common_tags
}

resource "aws_iam_role_policy_attachment" "backup_role_policy" {
  count = var.environment == "prod" ? 1 : 0

  role       = aws_iam_role.backup_role[0].name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSBackupServiceRolePolicyForBackup"
}

resource "aws_iam_role_policy_attachment" "backup_restore_role_policy" {
  count = var.environment == "prod" ? 1 : 0

  role       = aws_iam_role.backup_role[0].name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSBackupServiceRolePolicyForRestores"
}

# AWS Inspector Assessment Template (optional)
resource "aws_inspector_assessment_template" "main" {
  count = var.environment == "prod" ? 1 : 0

  name       = "${local.name}-assessment"
  target_arn = aws_inspector_assessment_target.main[0].arn
  duration   = 3600 # 1 hour

  rules_package_arns = [
    "arn:aws:inspector:${var.aws_region}:316112463485:rulespackage/0-9hgA516p"
  ]

  tags = local.common_tags
}

resource "aws_inspector_assessment_target" "main" {
  count = var.environment == "prod" ? 1 : 0

  name               = "${local.name}-assessment-target"
  resource_group_arn = aws_inspector_resource_group.main[0].arn

  tags = local.common_tags
}

resource "aws_inspector_resource_group" "main" {
  count = var.environment == "prod" ? 1 : 0

  tags = merge(local.common_tags, {
    Name = "${local.name}-inspector-resource-group"
  })
}
