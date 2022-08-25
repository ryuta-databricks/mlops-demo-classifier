# mlops-demo-classifier

This directory contains an ML project based on the
[Databricks MLOps Project Template](https://github.com/databricks/mlops-project-template).

## ML pipeline structure
This project defines an ML pipeline for automated retraining and batch inference of an ML model
on tabular data.

See the full pipeline structure below, and the [template README](https://github.com/databricks/mlops-project-template#ml-pipeline-structure-and-devloop)
for additional details.

![MLOps project template diagram](./doc-images/mlops-template-summary.png)


## Project structure
This project contains the following components:

| Component                  | Description                                                                                                                                                                       | Docs                                                       |
|----------------------------|-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|------------------------------------------------------------|
| ML Code                    | Unit tested Python modules and notebooks containing model training and inference code                                                                                             | [This file](#Getting-started)                              |
| ML Resource Config as Code | ML pipeline resource config (training and batch inference job schedules, etc) defined through [Terraform](https://docs.databricks.com/dev-tools/terraform/index.html) | [databricks-config/README.md](databricks-config/README.md) |
| CI/CD                      | [GitHub Actions](https://github.com/actions) workflows to test and deploy ML code and resources                                                                                   | [.github/workflows/README.md](.github/workflows/README.md) |
 
contained in the following files: 

```
├── steps              <- Python modules implementing ML pipeline logic, e.g. model training and evaluation. Most
│                         development work happens here.
│
├── notebooks          <- Databricks notebooks that call into the pipeline step modules under `steps`. Used to
│                         drive code execution on Databricks for CI/CD. In most cases, you do not need to modify
│                         these notebooks.
│
├── .github            <- Configuration folder for CI/CD using GitHub Actions. The CI/CD workflows run the notebooks
│                         under `notebooks` to test and deploy model training code
│
├── databricks-config  <- ML resource (ML jobs, MLflow models) config definitions expressed as code, across staging/prod
│   ├── staging
│   ├── prod
│
├── requirements.txt   <- Specifies Python dependencies for ML code (model training, batch inference, etc) 
│
├── tests              <- Tests for the modules under `steps`
```

## Getting started

Data scientists can get started right away iterating on and testing ML code under ``steps``.

We expect most development to take place  in `steps/train.py` (model training) and `steps/ingest.py`
(data loading and preprocessing). Search for TODOs in the code for pointers to the specific code to edit.

**NOTE**: If you're working on a regression problem, consider using [MLflow Pipelines](https://mlflow.org/docs/latest/pipelines.html)
for your ML code. MLflow Pipelines provides additional features (e.g. caching) and a declarative interface for
specifying ML pipeline configs that builds on top of the provided `steps`. You can incorporate MLflow Pipelines
into the current template by copying the contents of the [MLflow Pipelines Regression Template](https://github.com/mlflow/mlp-regression-template)
into the current repo. Replace the current `notebooks/Train.py` notebook with logic to run MLflow pipelines steps,
as shown in [this gist](https://gist.github.com/smurching/dd8c337412c58dba1ac18be1235b14cc). Then, follow [the docs](https://mlflow.org/docs/latest/pipelines.html)
to get started developing ML code.

### Developing on Databricks
You can iterate on ML code using [Repos](https://docs.databricks.com/repos/index.html). The provided
code examples require Databricks Runtime ML versions 10.5 and above. Using Databricks Repos also requires that you
push the template to a hosted Git repo and [set up git integration](https://docs.databricks.com/repos/set-up-git-integration.html).

If you'd like to iterate in your IDE but run code on Databricks, consider using the experimental
[dbx sync](https://dbx.readthedocs.io/en/latest/cli.html#dbx-sync) tool.

We recommend keeping your Python code modularized in unit-testable helper functions under ``steps``, iterating on the content
of functions and importing & invoking them in the provided notebooks for interactive development. This allows for
fast iteration while preserving testability of your ML code.

### Developing locally
You can also iterate on ML code locally. Be sure to install Python dependencies for local iteration
via `pip install -r requirements.txt -r test-requirements.txt`.

#### Trigger model training
Run `python steps/main.py` to trigger training.

#### Inspect results in the UI
To facilitate saving and sharing results from local iteration with collaborators, we recommend configuring your
environment to log to a Databricks MLflow tracking server, as described in [this guide](https://docs.databricks.com/applications/mlflow/access-hosted-tracking-server.html).
Then, update `profiles/local.yaml` (or `steps/main.py` if not using MLflow Pipelines) to use a Databricks tracking URI,
e.g. `databricks://<profile-name>` instead of a local `sqlite://` URI. You can then easily view model training results in the Databricks UI.

If you prefer to log results locally (the default), you can view model training results by running the MLflow UI:

```sh
mlflow ui \
   --backend-store-uri sqlite:///mlruns.db \
   --default-artifact-root ./mlruns \
   --host localhost
```

Then, open a browser tab pointing to [http://127.0.0.1:5000](http://127.0.0.1:5000)

#### Run unit tests
You can run unit tests for your ML code via `pytest tests`.

## Productionizing your ML project
After you've explored and validated the ML problem at hand, you may be ready to start productionizing your ML pipeline.
To do this, you or your ops team must follow the steps below:

### Create a hosted Git repo
Create a hosted Git repo to store project code, if you haven't already done so. From within the project
directory, initialize git and add your hosted Git repo as a remote:
```
git init --initial-branch=main
git remote add upstream <hosted-git-repo-url>
```

Commit the current README file to the `main` branch of the repo, to enable forking the repo:
```
git add README.md doc-images
git commit -m "Adding project README"
git push upstream main
```

### Configure CI/CD
If using GitHub Actions, follow the guide in [.github/workflows/README.md](.github/workflows/README.md) to
configure and enable CI/CD for the hosted Git repo created in the previous step.


If using another CI/CD provider, you can easily translate the provided (GitHub Actions YAML under `.github`) to other
CI/CD providers by running the same shell commands, with a few caveats:

* Usages of the `run-notebook` Action should be replaced by [installing the Databricks CLI](https://github.com/databricks/databricks-cli#installation)
  and invoking the `databricks runs submit --wait` CLI
  ([docs](https://docs.databricks.com/dev-tools/cli/runs-cli.html#submit-a-one-time-run)).
* The model deployment CD workflows in `deploy-model-prod.yml` and `deploy-model-staging.yml` are currently triggered
  by the `notebooks/TriggerModelDeploy.py` helper notebook after the model training job completes. This notebook
  hardcodes the API endpoint for triggering a GitHub Actions workflow. Update `notebooks/TriggerModelDeploy.py`
  to instead hit the appropriate REST API endpoint for triggering model deployment CD for your CI/CD provider.

### Merge a PR with your initial ML code
Open a PR adding the ML code to the repository. We recommend including all files outside of `databricks-config`
in this PR, e.g via `git add -- . ':!databricks-config'`

CI will run to ensure that tests pass on your initial ML code. Get your PR reviewed and merged

### Create release branch
Create and push a release branch called `release` off of the `main` branch of the repository:
```
git checkout -b release main
git push upstream release
```

Your production jobs (model training, batch inference) will pull ML code against this branch, while your staging jobs will pull ML code against the `main` branch. Note that the `main` branch will be the source of truth for ML resource configurations and CI/CD workflows.

For future ML code changes, iterate against the `main` branch and regularly deploy your ML code from staging to production by merging code changes from the `main` branch into the `release` branch.

### Deploy ML resources and enable production jobs
Follow the instructions in [databricks-config/README.md](databricks-config/README.md) to deploy ML resources
and production jobs.
