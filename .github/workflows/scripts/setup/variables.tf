variable "git_token" {
  type        = string
  description = "Git token used by the created service principal to checkout ML code to run during CI/CD. Must have read permissions on the Git repo containing the current ML project"
  sensitive = true
}

variable "git_provider" {
  type        = string
  description = "Hosted Git provider, as described in https://docs.databricks.com/dev-tools/api/latest/gitcredentials.html#operation/create-git-credential. For example, 'gitHub' if using GitHub."
}

variable "staging_profile" {
  type        = string
  description = "Name of Databricks CLI profile on the current machine configured to run against the staging workspace"
  default = "mlops-demo-classifier-staging"
}

variable "prod_profile" {
  type        = string
  description = "Name of Databricks CLI profile on the current machine configured to run against the prod workspace"
  default = "mlops-demo-classifier-prod"
}


