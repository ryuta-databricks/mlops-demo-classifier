terraform {
  // TODO: Configure remote state storage here using one of the backends described
  // https://www.terraform.io/language/settings/backends/configuration#available-backends,
  // otherwise resource deployment will fail.
  // The example `backend` block below configures the s3 backend
  // (docs: https://www.terraform.io/language/settings/backends/s3)
  // for storing Terraform state in an AWS S3 bucket:
  //
  //  backend "s3" {
  //    bucket = "mybucket"
  //    key    = "path/to/my/key"
  //    region = "us-east-1"
  //  }
  required_providers {
    databricks = {
      source = "databricks/databricks"
    }
  }
}
