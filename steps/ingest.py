import pandas as pd
from sklearn.model_selection import train_test_split
import os

def load_dataset(env):
    """
    Load the dataset for model training and evaluation
    :param env: Current environment ("dev", "staging", or "prod").
    :return: Tuple of (train_data, test_data, train_labels, test_labels)
    """
    # TODO: Update this logic to read data from your desired data source
    # In the example code below, we hardcode the path of a local dataset to read across all envs.
    # You can update this logic to read data from other sources, using the env input argument to write logic for
    # loading different datasets across environments (e.g. "staging.training_data" in staging and "prod.training_data"
    # in prod)
    repo_root = os.path.dirname(os.path.dirname(__file__))
    dataset_path = os.path.join(repo_root, "datasets", "IRIS.csv")
    pdf = pd.read_csv(dataset_path)
    X = pdf.drop('species', axis=1)
    y = pdf.species
    return train_test_split(X, y, test_size=0.2, random_state=9)
