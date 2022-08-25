module "azure_create_sp" {
  source = "databricks/mlops-azure-project-with-sp-creation/databricks"
  providers = {
    databricks.staging = databricks.staging
    databricks.prod = databricks.prod
    azuread = azuread
  }
  service_principal_name = "mlops-demo-classifier-cicd"
  project_directory_path = "/Users/ryuta.yoshimatsu@databricks.com/mlops-demo-classifier"
  azure_tenant_id        = var.azure_tenant_id
  service_principal_group_name = "mlops-demo-classifier-service-principals"
}

// Associate git credentials with the service principal
data "databricks_current_user" "staging_user" {
  provider = databricks.staging
}

provider "databricks" {
  alias = "staging_sp"
  host  = "https://e2-demo-emea.cloud.databricks.com/"
  token = module.azure_create_sp.staging_service_principal_aad_token
}

resource "databricks_git_credential" "staging_git" {
  provider              = databricks.staging_sp
  git_username          = "mlops-demo-classifier-cicd"
  git_provider          = var.git_provider
  personal_access_token = var.git_token
}

provider "databricks" {
  alias = "prod_sp"
  host  = "https://e2-demo-emea.cloud.databricks.com/"
  token = module.azure_create_sp.prod_service_principal_aad_token
}

resource "databricks_git_credential" "prod_git" {
  provider              = databricks.prod_sp
  git_username          = "mlops-demo-classifier-cicd"
  git_provider          = var.git_provider
  personal_access_token = var.git_token
}

// We produce the service princpal's application ID, client secret, and tenant ID as output, to enable
// extracting their values and storing them as secrets in your CI system
//
// If using GitHub Actions, you can create new repo secrets through Terraform as well
// e.g. using https://registry.terraform.io/providers/integrations/github/latest/docs/resources/actions_secret
output "STAGING_AZURE_SP_APPLICATION_ID" {
  value = module.azure_create_sp.staging_service_principal_application_id
  sensitive = true
}

output "STAGING_AZURE_SP_CLIENT_SECRET" {
  value = module.azure_create_sp.staging_service_principal_client_secret
  sensitive = true
}

output "STAGING_AZURE_SP_TENANT_ID" {
  value = var.azure_tenant_id
  sensitive = true
}

output "PROD_AZURE_SP_APPLICATION_ID" {
  value = module.azure_create_sp.prod_service_principal_application_id
  sensitive = true
}

output "PROD_AZURE_SP_CLIENT_SECRET" {
  value = module.azure_create_sp.prod_service_principal_client_secret
  sensitive = true
}

output "PROD_AZURE_SP_TENANT_ID" {
  value = var.azure_tenant_id
  sensitive = true
}
