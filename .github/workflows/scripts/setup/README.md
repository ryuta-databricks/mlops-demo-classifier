# CI/CD Setup Helper Scripts
This directory contains helper scripts for setting up CI/CD using GitHub Actions. The scripts
automatically generate the secrets used by the provided workflows under `.github/workflows`.
After running the provided scripts, you can store the generated secrets as [GitHub Actions
secrets](../../README.md#store-secrets-for-databricks-rest-api-auth) to complete the CI/CD setup process.


It contains:

* ``create_service_principals.py``: Python script to run to create service principals with
   the necessary Git credentials and permissions configured in Databricks for CI/CD.
* ``*.tf``: Terraform config files defining the resources provisioned by the `create_service_principals.py`
   script. If you frequently start new production ML projects, consider automating the creation
   of new Git repos with CI/CD preconfigured using Terraform and these files.

## Prerequisites

To use the scripts, you must:
* Be a Databricks workspace admin in the staging and prod workspaces. Verify that you're an admin by viewing the
  [staging workspace admin console](https://e2-demo-emea.cloud.databricks.com/#setting/accounts) and
  [prod workspace admin console](https://e2-demo-emea.cloud.databricks.com/#setting/accounts). If
  the admin console UI loads instead of the Databricks workspace homepage, you are an admin.
* Be able to create Git tokens with permission to check out the current repository


### Install CLIs
* Install the [Terraform CLI](https://learn.hashicorp.com/tutorials/terraform/install-cli)
* Install the [Databricks CLI](https://github.com/databricks/databricks-cli): ``pip install databricks-cli``
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
The setup script prompts for and stores a Git token in Databricks. This token is used to fetch ML code from
the current repo to run on Databricks for CI/CD (e.g. to check out code from a PR branch and run it
during CI/CD). Generate a Git token with permissions to check out the current repository. If using
GitHub as your hosted Git provider, you can do this through the [token UI](https://github.com/settings/tokens/new);
be sure to generate a token with "Repo" scope. Note the expiry date of the token upon creation. 

## Usage

### First-time setup
From the current directory (`.github/workflows/scripts/setup`), run

```
$ ./create_service_principals.py secrets-file-path
```

where `secrets-file-path` is the path to a file to which to write CI/CD secrets created
by the shell script in JSON format. The shell command will prompt you for
an input Git token and git provider.
After the script runs, store the secret values in `secrets-file-path` as GitHub Actions secrets
for use in CI/CD workflows, as described in [.github/workflows/README.md](../../README.md#store-secrets-for-databricks-rest-api-auth)
The generated
Databricks service principal REST API tokens have an [expiry of 100 days](https://github.com/databricks/terraform-databricks-mlops-aws-project#mlops-aws-project-module)
and will need to be rotated thereafter.

If the resulting service principals are misconfigured (e.g. don't work in CI/CD), you can run
`terraform destroy` within the current directory (`.github/workflows/scripts/setup`) to delete them.

Running the script will produce `.tfstate` files in the current directory. These Terraform state files
track the service principals and tokens that were created and are important for enabling
token rotation and updates. They're also sensitive and should not be checked into version control.
Therefore we encourage you to follow the directions in `provider.tf` to configure and store these state files
in a [remote state backend](https://www.terraform.io/language/settings/backends/configuration#backend-configuration),
to facilitate token rotation.

Alternatively, you can discard the state files and create new service
principals and tokens by rerunning the script in the future. This is simpler but may result in
accruing new service principals in your staging and prod workspaces over time. If you choose this approach,
take care to ensure that the `mlops-demo-classifier-service-principals` group has `CAN_MANAGE`
permissions on the resources defined under `databricks-config`, so that new service principals created for
the project can manage any existing ML resources.  You can verify these permission settings in
`permissions.tf` files under `databricks-config`.

### Updating, rotating, regenerating secrets
You can regenerate secret values or update e.g. the Git token used by the CI/CD service principals by
rerunning the `create_service_principals.py` script. Simply rerunning the script with previously-used
parameters will automatically regenerate any expired
Databricks service principal REST API tokens,
writing their values to the provided output file path. You must also rerun the script and supply
a new Git token before the original expires to ensure CI/CD continues to work.
