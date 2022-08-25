locals {
  // Base workspace directory under which to create resources in the workspace for the current MLOps project
  // We assume the service principal used to deploy resources has CAN MANAGE permissions on directory
  // You may need to modify this value if you'd like to use a different directory for per-project resources
  mlflow_experiment_parent_dir = "/Users/ryuta.yoshimatsu@databricks.com/mlops-demo-classifier"
  // Current environment
  env = "prod"
  // Env-specific prefix to prepend to resource names. We recommend creating staging/prod resources
  // in separate workspaces to isolate prod resources from code running in CI, but this prefix
  // unblocks using a shared workspace across envs.
  env_prefix = "${local.env}-"
  // User group to give read permissions for the batch inference and model training jobs
  read_user_group = "users"
  // (Optional) Application ID for the staging service principal. Specify this and
  // pass it to the job cluster definitions in training-job.tf, batch-job.tf to enable your 
  // model training and batch inference jobs to read/write data from the Unity Catalog
  // sp_app_id = <application ID>
}
