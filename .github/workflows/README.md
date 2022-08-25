# CI/CD Workflow Definitions
This directory contains CI/CD workflow definitions using [GitHub Actions](https://docs.github.com/en/actions),
under ``workflows``. These workflows cover testing and deployment of both ML code (for model training, batch inference, etc) and the 
Databricks ML resource definitions under ``databricks-config``.
 
## Configuring CI/CD
This section covers first-time setup of CI/CD.

### Prerequisites

The steps below require [Databricks workspace admin permissions](https://docs.databricks.com/administration-guide/index.html) in the staging and prod workspaces.


### Recommended: provision CI/CD service principals through script
We recommend running the setup script under `.github/workflows/scrips/setup` to
create service principals, Databricks git credentials, and API tokens for CI/CD. See
[.github/workflows/scripts/setup/README.md](scripts/setup/README.md)
for details. The script is agnostic to CI/CD provider, i.e. it creates and configures service principals
that you can use with any CI/CD provider. It also uses Terraform, so you can reuse the underlying
Terraform configs to build automation for configuring CI/CD for new ML projects and perform
secret rotation automatically.

### Alternative: manually provision CI/CD service principals
If you are unable to follow the recommended shell script approach to setting up CI/CD,
you can also configure it manually as shown below:

#### Create service principals

[Create a service principal](https://docs.databricks.com/dev-tools/api/latest/scim/scim-sp.html#create-service-principal)
in both the staging and prod workspaces, with the ``allow_cluster_create``
[entitlement](https://docs.databricks.com/administration-guide/users-groups/service-principals.html#manage-entitlements-for-a-service-principal)


#### Grant permissions to service principals

Grant token usage permissions to the service principals [via the UI](https://docs.databricks.com/administration-guide/access-control/tokens.html#manage-token-permissions-using-the-admin-console)
or [REST API](https://docs.databricks.com/administration-guide/access-control/tokens.html#manage-token-permissions-using-the-permissions-api).
Then, grant the service principals ["Can Manage" permissions](https://docs.databricks.com/security/access-control/workspace-acl.html#folder-permissions) on the workspace directory `/Users/ryuta.yoshimatsu@databricks.com/mlops-demo-classifier`
in both staging and prod, creating the workspace directory if it does not exist.


#### Generate tokens on behalf of service principals

[Create tokens](https://docs.databricks.com/administration-guide/users-groups/service-principals.html#manage-access-tokens-for-a-service-principal)
on behalf of the service principals from the previous step.


#### Configure Git credentials
Obtain a set of Git credentials with read permissions on the hosted Git repository for
the current project.

Then, using the service principal Databricks REST API tokens from the previous section, hit the 
[Git credentials REST API](https://docs.databricks.com/dev-tools/api/latest/gitcredentials.html#operation/create-git-credential)
to associate the Databricks service principal with the Git credentials you found.

### Store secrets for Databricks REST API auth
To use the provided CI/CD workflows as is, you must configure the secrets listed below
as [GitHub Actions Encrypted Secrets](https://docs.github.com/en/actions/security-guides/encrypted-secrets#creating-encrypted-secrets-for-a-repository).
You can also modify the workflows to read secrets from elsewhere.

To use the provided CI/CD workflows as is, you must configure the secrets listed below
as [GitHub Actions Encrypted Secrets](https://docs.github.com/en/actions/security-guides/encrypted-secrets#creating-encrypted-secrets-for-a-repository). The workflows assume that you will configure [repo secrets](https://docs.github.com/en/actions/security-guides/encrypted-secrets#creating-encrypted-secrets-for-a-repository), but you can also use [environment secrets](https://docs.github.com/en/actions/security-guides/encrypted-secrets#creating-encrypted-secrets-for-an-environment) to restrict access to production secrets. You can also modify the workflows to read secrets from another secret provider.


* `STAGING_WORKSPACE_TOKEN`, `PROD_WORKSPACE_TOKEN`: API tokens of the service principals added to the staging and prod Databricks workspaces in previous steps

* `TRIGGER_WORKFLOWS_GITHUB_TOKEN`: [GitHub PAT token](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/creating-a-personal-access-token#creating-a-token)
   with write permissions on the current repo. This token is stored in Databricks
   and is used to trigger GitHub Actions CD workflows when events occur in
   Databricks. In particular, we use the token to trigger a GitHub Actions CD workflow for model validation and
   deployment when the Databricks model training job completes, i.e. perform step (2) in
   [this diagram](https://github.com/databricks/mlops-project-template/blob/main/Pipeline.md#model-training-pipeline).
   Note: To update the token value (e.g. when the token is near expiry), you must both update its value in GitHub
   Actions Secrets and manually trigger the "Terraform Deployment for mlops-demo-classifier" CD workflow,
   to update the value of the token stored in Databricks.


See also [these docs](https://github.com/databricks/run-notebook/blob/main/README.md#prerequisites)
for for the ``run-notebook`` GitHub Action used to drive CI/CD for additional context on the above secrets.

### Configure secrets for ML resource CI/CD
**Note**: You can safely skip this step and return to it after your first ML code is merged into your
hosted Git repository and you're ready to deploy production ML training jobs.

As described in [databricks-config/README.md](../../databricks-config/README.md), you must configure a Terraform remote
state backend for storing ML resource state via edits to `provider.tf` files.

After configuring your remote backend and testing authentication,
store any necessary credentials as GitHub Actions secrets.
Then, update the `terraform-cd.yml` and `terraform-ci.yml` workflows to use the secrets before invoking `terraform`
CLI commands. The relevant places to configure auth for your Terraform backend are marked with TODOS in the workflow
files.

### Add GitHub workflows to hosted Git repo 
Open and merge a PR adding the GitHub Actions workflows under `.github` to your hosted Git repo so that they run on subsequent pull requests, [enable Actions](https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/enabling-features-for-your-repository/managing-github-actions-settings-for-a-repository)
in your repo, and [create environments](https://docs.github.com/en/actions/deployment/targeting-different-environments/using-environments-for-deployment#creating-an-environment)
named "staging" and "prod"

## Next steps
In this template, interactions with the staging and prod workspace are driven through CI/CD. After you've configured
CI/CD, you can productionize your ML project by testing and deploying ML code, deploying model training and
inference jobs, and more. See the [main project README](../../README.md#productionizing-your-ml-project) for details.
