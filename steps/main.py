"""
This module allows for local execution of model training code.
"""
import mlflow
from utils import set_experiment
from train import fit_model
from ingest import load_dataset

def main(env, test_mode):
    X_train, X_test, y_train, y_test = load_dataset(env)
    set_experiment(env, test_mode)
    return fit_model(X_train, X_test, y_train, y_test)


if __name__ == "__main__":
    # TODO: this line configures the training script to log runs and models to a local sqlite database
    # For sharability and durability of model training results from local development, we encourage
    # logging to the Databricks-hosted MLflow tracking server in your development workspace.
    # See https://docs.databricks.com/applications/mlflow/access-hosted-tracking-server.html
    # for details
    mlflow.set_tracking_uri("sqlite:///mlruns.db")
    logged_model_uri = main("dev", test_mode=False)
    print(f"Trained model and logged it as an MLflow run artifact with URI '{logged_model_uri}'")
