resource "databricks_mlflow_model" "registered_model" {
  name        = "${local.env_prefix}mlops-demo-classifier-model"
  description = "My MLflow model description"
}
