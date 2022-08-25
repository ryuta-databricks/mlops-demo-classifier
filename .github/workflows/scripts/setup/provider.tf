terraform {
  required_providers {
    databricks = {
      source  = "databricks/databricks"
      version = ">= 0.5.8"
    }
    }
  // Consider configuring remote state storage here using one of the backends described
  // https://www.terraform.io/language/settings/backends/configuration#available-backends,
  // to facilitate token rotation and management in the future
  // The example `backend` block below configures the s3 backend
  // (docs: https://www.terraform.io/language/settings/backends/s3)
  // for storing Terraform state in an AWS S3 bucket:
  //
  //  backend "s3" {
  //    bucket = "mybucket"
  //    key    = "path/to/my/key"
  //    region = "us-east-1"
  //  }
  }

provider "databricks" {
  alias = "staging"
  profile = var.staging_profile
}

provider "databricks" {
  alias = "prod"
  profile = var.prod_profile
}

