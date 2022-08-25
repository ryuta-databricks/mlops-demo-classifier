# MLOps Template Setup Scripts
This directory contains setup scripts intended to automate CI/CD and ML resource config setup
for MLOps engineers.

The scripts set up CI/CD with GitHub Actions. If using another CI/CD provider, you can
easily translate the provided CI/CD workflows (GitHub Actions YAML under `.github/workflows`)
to other CI/CD providers by running the same shell commands, with a few caveats:

* Usages of the `run-notebook` Action should be replaced by [installing the Databricks CLI](https://github.com/databricks/databricks-cli#installation)
  and invoking the `databricks runs submit --wait` CLI
  ([docs](https://docs.databricks.com/dev-tools/cli/runs-cli.html#submit-a-one-time-run)).
* The model deployment CD workflows in `deploy-model-prod.yml` and `deploy-model-staging.yml` are currently triggered
  by the `notebooks/TriggerModelDeploy.py` helper notebook after the model training job completes. This notebook
  hardcodes the API endpoint for triggering a GitHub Actions workflow. Update `notebooks/TriggerModelDeploy.py`
  to instead hit the appropriate REST API endpoint for triggering model deployment CD for your CI/CD provider.




## Prerequisites

### Install CLIs
* Install the [Terraform CLI](https://learn.hashicorp.com/tutorials/terraform/install-cli)
* Install the [Databricks CLI](https://github.com/databricks/databricks-cli): ``pip install databricks-cli``

* Install AWS CLI: ``pip install awscli``


### Verify permissions
To use the scripts, you must:
* Be a Databricks workspace admin in the staging and prod workspaces. Verify that you're an admin by viewing the
  [staging workspace admin console](https://e2-demo-emea.cloud.databricks.com/#setting/accounts) and
  [prod workspace admin console](https://e2-demo-emea.cloud.databricks.com/#setting/accounts). If
  the admin console UI loads instead of the Databricks workspace homepage, you are an admin.
* Be able to create Git tokens with permission to check out the current repository
  * Have permission to manage AWS IAM users and attached IAM policies (`"iam:*"` permissions) in the current AWS account.
  If you lack sufficient permissions, you'll see an error message describing any missing permissions when you
  run the setup scripts below. If that occurs, contact your AWS account admin to request any missing permissions.


### Configure AWS auth
* After verifying that your AWS user has permission to manage IAM users and policies,
  follow [these docs](https://docs.aws.amazon.com/general/latest/gr/aws-sec-cred-types.html#access-keys-and-secret-access-keys)
  to generate an AWS access key.
* Run `aws configure --profile mlops-demo-classifier` to configure an AWS CLI profile, passing the access key ID and secret access key from the previous step
* Run `export AWS_PROFILE=mlops-demo-classifier` to indicate to Terraform that it should use the newly-created AWS CLI profile
  to authenticate to AWS
### Configure Databricks auth
* Ensure you are a Databricks workspace admin in the staging and prod workspaces.
  To do this, verify you can view the
  [staging workspace admin console](https://e2-demo-emea.cloud.databricks.com/#setting/accounts) and
  [prod workspace admin console](https://e2-demo-emea.cloud.databricks.com/#setting/accounts)
* Create [Databricks REST API tokens](https://docs.databricks.com/dev-tools/api/latest/authentication.html#generate-a-personal-access-token)
  in the staging and prod workspaces.
* Run the shell commands below to configure Databricks CLI profiles for your staging and prod workspaces. Supply the tokens
  created in the previous step when prompted:
    * ``databricks configure --token --profile "mlops-demo-classifier-staging" --host https://e2-demo-emea.cloud.databricks.com/ ``
    * ``databricks configure --token --profile "mlops-demo-classifier-prod" --host https://e2-demo-emea.cloud.databricks.com/``

### Set up service principal user group
Ensure a group named `mlops-demo-classifier-service-principals` exists in the staging and prod workspace, e.g.
by checking for the group in the [staging workspace admin console](https://e2-demo-emea.cloud.databricks.com/#setting/accounts/groups) and
[prod workspace admin console](https://e2-demo-emea.cloud.databricks.com/#setting/accounts/groups).
Create the group in staging and/or prod as needed.
Then, grant the `mlops-demo-classifier-service-principals` group [token usage permissions](https://docs.databricks.com/administration-guide/access-control/tokens.html#manage-token-permissions-using-the-admin-console)
### Obtain a git token for use in CI/CD
The setup script prompts a Git token with both read and write permissions
on the current repo.

This token is used to:
1. Fetch ML code from the current repo to run on Databricks for CI/CD (e.g. to check out code from a PR branch and run it
during CI/CD).
2. Call back from
   Databricks -> GitHub Actions to trigger a model deployment deployment workflow when
   automated model retraining completes, i.e. perform step (2) in
   [this diagram](https://github.com/databricks/mlops-project-template/blob/main/Pipeline.md#model-training-pipeline).

If using GitHub as your hosted Git provider, you can generate a Git token through the [token UI](https://github.com/settings/tokens/new);
be sure to generate a token with "Repo" scope.

## Usage

### Run the scripts
From the repo root directory, run:

```
# Set AWS_REGION environment variable to your desired AWS region for storing
# terraform state, e.g. "us-east-1" to store Terraform state in S3 buckets in us-east-1
export AWS_REGION="us-east-1"
python .mlops-setup-scripts/terraform/bootstrap.py
# Alternatively, run `python .mlops-setup-scripts/cicd/bootstrap.py`,
# which will prompt you for inputs
python .mlops-setup-scripts/cicd/bootstrap.py \
--var git_provider=gitHub \
  --var github_repo_url=https://github.com/<your-org>/<your-repo-name> \
  --var git_token=<your-git-token>
```

Take care to run the Terraform bootstrap script before the CI/CD bootstrap script. This will:


1. Create an AWS S3 bucket and DynamoDB table for storing ML resource config (job, MLflow experiment, etc) state for the
   current ML project
2. Create another AWS S3 bucket and DynamoDB table for storing the state of CI/CD principals provisioned for the current
   ML project. 
3. Write credentials for accessing the S3 bucket and Dynamo DB table in (1) to a file.
4. Create Databricks service principals configured for CI/CD, write their credentials to a file, and store their
   state in the S3 bucket and DynamoDB table created in (2). 


Each `bootstrap.py` script will print out the path to a JSON file containing generated secret values
to store for CI/CD. **Note the paths of these secrets files for subsequent steps.** If either script
fails or the generated resources are misconfigured (e.g. you supplied invalid Git credentials for CI/CD
service principals when prompted), simply rerun and supply updated input values.

### Store generated secrets in CI/CD
Store each of the generated secrets in the output JSON files as
[GitHub Actions Encrypted Secrets](https://docs.github.com/en/actions/security-guides/encrypted-secrets#creating-encrypted-secrets-for-a-repository),
where the JSON key
(e.g. `PROD_WORKSPACE_TOKEN`)
is the expected name of the secret in GitHub Actions and the JSON value
is the value of the secret. 

Note: The provided GitHub Actions workflows under `.github/workflows` assume that you will configure
[repo secrets](https://docs.github.com/en/actions/security-guides/encrypted-secrets#creating-encrypted-secrets-for-a-repository),
but you can also use
[environment secrets](https://docs.github.com/en/actions/security-guides/encrypted-secrets#creating-encrypted-secrets-for-an-environment)
to restrict access to production secrets. You can also modify the workflows to read secrets from another
secret provider.

### Add GitHub workflows to hosted Git repo
Open and merge a PR adding the GitHub Actions workflows under `.github` to your hosted Git repo so that they run on subsequent pull requests, [enable Actions](https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/enabling-features-for-your-repository/managing-github-actions-settings-for-a-repository)
in your repo, and [create environments](https://docs.github.com/en/actions/deployment/targeting-different-environments/using-environments-for-deployment#creating-an-environment)
named "staging" and "prod"

### Secret rotation
The generated CI/CD
Databricks service principal REST API tokens have an [expiry of 100 days](https://github.com/databricks/terraform-databricks-mlops-aws-project#mlops-aws-project-module)
and will need to be rotated thereafter. To rotate CI/CD secrets after expiry, simply rerun `python .mlops-setup-scripts/cicd/bootstrap.py`
with updated inputs, after configuring auth as described in the prerequisites.

## Next steps
In this template, interactions with the staging and prod workspace are driven through CI/CD. After you've configured
CI/CD and ML resource state storage, you can productionize your ML project by testing and deploying ML code, deploying model training and
inference jobs, and more. See the [main project README](../README.md#productionizing-your-ml-project) for details.
