from sklearn.base import BaseEstimator
import pytest
import mlflow

from steps.train import estimator_fn, fit_model
from steps.ingest import load_dataset

def test_type():
    estimator = estimator_fn()
    assert isinstance(estimator, BaseEstimator)


@pytest.fixture(autouse=True)
def log_mlflow_data_to_tmpdir(tmpdir):
    """
    Fixture that configures MLflow to log data (runs etc) to a temporary directory during tests,
    to avoid polluting the local filesystem
    """
    mlflow.set_tracking_uri(tmpdir.strpath)
    mlflow.set_experiment("Temporary experiment for unit tests")


@pytest.mark.parametrize("env", ["dev", "staging", "prod"])
def test_fit_model(env):
    # Verify that we can fit the model and load it back for inference
    X_train, X_test, y_train, y_test = load_dataset(env)
    logged_model_uri = fit_model(X_train, X_test, y_train, y_test)
    loaded_model = mlflow.pyfunc.load_model(logged_model_uri)
    loaded_model.predict(X_train)
