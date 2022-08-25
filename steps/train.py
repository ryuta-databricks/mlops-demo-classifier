from sklearn.svm import SVC
from sklearn.model_selection import GridSearchCV

import mlflow

def estimator_fn():
  """
  Return a sklearn estimator capable of inference on the training dataset
  :return:
  """
  # TODO: Update this logic to configure an appropriate estimator for model training. Add
  # feature transformation logic here e.g. as part of an sklearn pipeline, so that any feature
  # transformation logic can be shared between training and inference
  estimator = SVC()
  parameters = {'kernel':('linear', 'rbf'), 'C':[1, 10]}
  estimator = GridSearchCV(estimator, parameters)
  return estimator


def fit_model(X_train, X_test, y_train, y_test):
  """
  Fit and evaluate a model on the provided train & test datasets,
  returning the URI of the logged MLflow model
  """
  mlflow.sklearn.autolog(log_input_examples=True, silent=True)
  estimator = estimator_fn()
  with mlflow.start_run() as run:
    estimator.fit(X_train, y_train)
    mlflow.sklearn.eval_and_log_metrics(estimator, X_test, y_test, prefix="test_")
  # MLflow automatically logs the model to the run as an artifact under /model
  return f"runs:/{run.info.run_id}/model"
