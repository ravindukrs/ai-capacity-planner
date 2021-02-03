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

import numpy as np
import application.constants as const
from application.load_model import get_model
import pymc3 as pm
from application.logging_handler import logger

seed = 42
np.random.seed(42)


class BayesianPolynomialRegressor:

    __instance = None

    @staticmethod
    def getInstance():
        if BayesianPolynomialRegressor.__instance is None:
            BayesianPolynomialRegressor()
        return BayesianPolynomialRegressor.__instance

    def __init__(self):
        if BayesianPolynomialRegressor.__instance is not None:
            logger.exception("Tried to reassign instance in "
                             "regressor.py. Invalid operation")
            raise Exception("Instance already assigned")
        else:
            model = get_model()
            self.poly_model = model["model"]
            self.trace = model["trace"]
            self.x_shared = model["x_shared"]
            self.f_pred = model["f_pred"]
            self.scaler = model["scaler"]
            self.encoder = model["encoder"]
            self.gp = model["gp"]
            del model

            BayesianPolynomialRegressor.__instance = self

    def predict(self, sample_count=const.DEFAULT_SAMPLE_COUNT):
        """
        Predict by Sampling.
        :param sample_count:
        :return prediction:
        """
        with self.poly_model:
            pred_samples = pm.sample_posterior_predictive(
                self.trace, vars=[self.f_pred],
                samples=sample_count,
                random_seed=seed
            )
            y_pred = pred_samples["f_pred"].mean(axis=0), \
                pred_samples["f_pred"].std(axis=0)
            return y_pred

    def predict_gp(self):
        """
        Predict by obtaining analytical mean.
        :return mean as prediction:
        """
        mu, var = self.gp.predict(
            Xnew=self.x_shared,
            point=self.trace[0],
            diag=True
        )
        return mu

    def predict_point(self, data, method=None,
                      sample_count=const.DEFAULT_SAMPLE_COUNT):
        """
        Get TPS prediction for a single data point
        Set data for prediction as a shared variable.
        all appropriate prediction method.
        :param data: Concurrency and Message Size
        :return TPS and Little's law Latency:
        """
        x_val = data
        x_val[0] = self.encoder.transform([x_val[0]])[0]
        x_val = self.scaler.transform([x_val])

        self.x_shared.set_value(x_val)

        if method == const.NO_SAMPLING:
            prediction = self.predict_gp()
            return prediction[0]
        else:
            prediction = self.predict(sample_count=sample_count)
            return prediction

    def max_tps(self, data, method=const.NO_SAMPLING,
                sample_count=const.DEFAULT_SAMPLE_COUNT):
        """
        Get maximum TPS prediction for a given scenario and message size
        Set data for prediction as a shared variable. Call appropriate
        prediction method.
        :param data: Scenario and Message Size
        :return TPS and Little's law Latency:
        """
        prediction_data_list = []
        scenario = data[0]
        message_size = data[1]
        max_tps_concurrency = 1

        for concurrency in range(0, const.MAX_CONCURRENCY,
                                 const.CONCURRENCY_STEP):
            if concurrency == 0:
                prediction_data_list.append([scenario, 1, message_size])
            else:
                prediction_data_list.append(
                    [scenario, concurrency, message_size]
                )

        data_array = np.array(prediction_data_list)
        data_array[:, 0] = self.encoder.transform(data_array[:, 0])
        data_array = self.scaler.transform(data_array)

        self.x_shared.set_value(data_array)

        if method == const.NO_SAMPLING:
            predictions = self.predict_gp()
            index = np.argmax(predictions)
            if index != 0:
                max_tps_concurrency = const.CONCURRENCY_STEP * index
            return max(predictions), max_tps_concurrency

        else:
            predictions = self.predict(sample_count=sample_count)
            index = np.argmax(predictions)
            if index != 0:
                max_tps_concurrency = const.CONCURRENCY_STEP * index
            return max(predictions[0]), max_tps_concurrency


def get_regressor():
    return BayesianPolynomialRegressor.getInstance()
