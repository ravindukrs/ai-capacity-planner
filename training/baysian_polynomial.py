"""
 Copyright (c) 2021, WSO2 Inc. (http://www.wso2.com). All Rights Reserved.
  This software is the property of WSO2 Inc. and its suppliers, if any.
  Dissemination of any information or reproduction of any material contained
  herein is strictly forbidden, unless permitted by WSO2 in accordance with
  the WSO2 Commercial License available at http://wso2.com/licenses.
  For specific language governing the permissions and limitations under
  this license, please see the license as well as any agreement you’ve
  entered into with WSO2 governing the purchase of this software and any
"""

import math
import numpy as np
import pandas as pd
import csv
from sklearn.preprocessing import MinMaxScaler
from sklearn.preprocessing import LabelEncoder
from sklearn.utils import shuffle
from sklearn.model_selection import KFold
import pymc3 as pm
from sklearn.metrics import mean_squared_error


def root_mean_squared_percentage_error(y_true, prediction):
    """
    Calculate root mean squared percentage error of
    predictions compared to y_values from dataset.
    :param y_true: y_values (actual TPS) from Dataset
    :param prediction: predicted TPS
    :return rmspe: Root mean squared percentage error:
    """
    y_true, y_pred = np.array(y_true), np.array(prediction)
    EPSILON = 1e-10
    rmspe = (np.sqrt(np.mean(np.square((y_true - y_pred) /
                                       (y_true + EPSILON))))) * 100
    return rmspe


# Define MAPE function
def mean_absolute_percentage_error(y_true, prediction):
    """
    Calculate mean absolute percentage error of
    predictions compared to y_values from dataset.
    :param y_true: y_values (actual TPS) from Dataset
    :param prediction: predicted TPS
    :return rmspe: Mean Absolute Percentage error:
    """
    y_true, y_pred = np.array(y_true), np.array(prediction)
    mape = np.mean(np.abs((y_true - y_pred) / y_true)) * 100
    return mape


class BayesianPolyRegression:
    def fit(self, X, Y):
        with pm.Model() as self.model:
            lm = pm.Gamma("l", alpha=2, beta=1)
            offset = 0.1
            nu = pm.HalfCauchy("nu", beta=1)
            d = 2

            cov = nu ** 2 * pm.gp.cov.Polynomial(X.shape[1], lm, d, offset)

            self.gp = pm.gp.Marginal(cov_func=cov)

            sigma = pm.HalfCauchy("sigma", beta=1)
            self.gp.marginal_likelihood("y", X=X, y=Y, noise=sigma)

            self.map_trace = [pm.find_MAP()]

    def predict(self, X, with_error=False):
        with self.model:
            f_pred = self.gp.conditional('f_pred', X)
            pred_samples = pm.sample_posterior_predictive(
                self.map_trace, vars=[f_pred],
                samples=2000,
                random_seed=42
            )
            y_pred, uncer = pred_samples['f_pred'].mean(axis=0), \
                pred_samples['f_pred'].std(axis=0)

        if with_error:
            return y_pred, uncer / 1000
        return y_pred


def get_fold_predictions(X, y, eval_X):
    lr = BayesianPolyRegression()
    lr.fit(X, y)
    pred_y, error = lr.predict(eval_X, True)

    return pred_y, error


def run_baysian_poly():
    predict_label = 9  # 9 for TPS

    # Read Data
    dataset = pd.read_csv('dataset/dataset.csv')

    # Ignore Errors
    dataset = dataset.loc[dataset["Error %"] < 5]

    # Define X and Y columns
    X = dataset.iloc[:, [0, 2, 3]].values
    Y = dataset.iloc[:, predict_label].values

    # Encode 'Scenario Name'
    le_X_0 = LabelEncoder()
    X[:, 0] = le_X_0.fit_transform(X[:, 0])

    # Create Scaler
    scaler = MinMaxScaler(feature_range=(0, 1))

    # Apply Scaler on X
    scaler.fit(X)
    X = scaler.transform(X)

    # Convert Y to 1D Array - Not necessary
    Y = Y.flatten()

    # Shuffle Data
    X, Y = shuffle(X, Y, random_state=42)

    predictions = []
    errorlist = []
    y_actual = []

    kf = KFold(n_splits=10)

    for train_index, test_index in kf.split(X):
        pred_bayes, error = get_fold_predictions(np.copy(X[train_index]),
                                                 np.copy(Y[train_index]),
                                                 np.copy(X[test_index]))

        for item in pred_bayes:
            predictions.append(item)

        for item in error:
            errorlist.append(item)

        for item in Y[test_index]:
            y_actual.append(item)

        RMSPE = root_mean_squared_percentage_error(y_actual, predictions)
        MAPE = mean_absolute_percentage_error(y_actual, predictions)
        RMSE = math.sqrt(mean_squared_error(y_actual, predictions))

        print(
            "Scores for Baysian_Polynomial: \n",
            "RMSE :", RMSE, "\n",
            "MAPE: ", MAPE, "\n",
            "RMSPE: ", RMSPE, "\n",
        )

        file_name = "results/" + "baysian_poly.csv"
        with open(file_name, "a") as f:
            writer = csv.writer(f)
            writer.writerows(zip(y_actual, predictions))


# Run Evaluation
run_baysian_poly()
