# Databricks notebook source
##################################################################################
# Model Training Notebook
##
# This notebook trains and registers an MLflow model in the model registry.
# It's run as part of CI (to integration-test model training logic) and by an automated model training job
# defined under ``databricks-config``
#
# NOTE: In general, we recommend that you do not modify this notebook directly, and instead update data-loading
# and model training logic in Python modules under the `steps` directory.
# Modifying this notebook can break model training CI/CD.
#
# However, if you do need to make changes, be sure to preserve the following interface expected by CI and the
# production model training job:
#
# Parameters:
#
# * env (optional): Name of the environment the notebook is run in (dev, staging, or prod). Defaults to "dev".
#                   You can add environment-specific logic to this notebook based on the value of this parameter,
#                   e.g. read training data from different tables or data sources across environments.
# * test_mode (optional): Whether the current notebook is running in "test" mode. If True, an extra "test" suffix is
#                         added to the names of MLflow experiments and registered models used for training. This
#                         separates the potentially many runs/models logged during integration tests from
#                         runs/models produced by staging/production model training jobs. Defaults to False
#
# Return values:
# * model_uri: The notebook must return the URI of the registered model as notebook output specified through
#              dbutils.notebook.exit() AND as a task value with key "model_uri" specified through
#              dbutils.jobs.taskValues(...), for use by downstream notebooks.
##################################################################################

# COMMAND ----------
# MAGIC %load_ext autoreload
# MAGIC %autoreload 2

# COMMAND ----------
dbutils.widgets.dropdown("env", "dev", ["dev", "staging", "prod"], "Environment Name")
dbutils.widgets.dropdown("test_mode", "False", ["True", "False"], "Test Mode")

# COMMAND ----------
import sys
sys.path.append("../steps")

# COMMAND ----------
env = dbutils.widgets.get("env")
_test_mode = dbutils.widgets.get("test_mode")
test_mode = True if _test_mode.lower() == "true" else False

# COMMAND ----------
from main import main
logged_model_uri = main(env, test_mode)

# COMMAND ----------
from utils import get_model_name
import mlflow
model_name = get_model_name(env, test_mode)
model_version = mlflow.register_model(logged_model_uri, model_name)

# COMMAND ----------
model_uri = f"models:/{model_version.name}/{model_version.version}"
dbutils.jobs.taskValues.set("model_uri", model_uri)
dbutils.notebook.exit(model_uri)
