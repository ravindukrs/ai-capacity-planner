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

import unittest
from unittest import mock
import json
from application.capacity_planner_service import ai_capacity_planner
from application.regressor import get_regressor
from application.response_formatter import formatter, json_value_validator
import application.constants as const


class TestCapacityPlanner(unittest.TestCase):

    # Tests for Response Formatter (Round TPS or Calculate Little's Law Latency)
    def test_response_formatter_tps_negetive(self):
        tps = formatter(-1);
        self.assertEqual(2.220446049250313e-16, tps)

    def test_response_formatter_tps_latency_negetive(self):
        tps, latency = formatter(-1, 5);
        self.assertEqual(2.220446049250313e-16, tps)
        self.assertEqual(2.251799813685248e+19, latency)

    def test_response_formatter_tps_latency(self):
        tps, latency = formatter(1321.32132433234, 50);
        self.assertEqual(1321.32, tps)
        self.assertEqual(37.84, latency)

    # Tests for Request Validator
    def test_json_value_validator_valid_point_pred(self):
        is_valid, error = json_value_validator(scenario="Passthrough", concurrency=100,
                         message_size=1200)
        self.assertEqual(True, is_valid)
        self.assertEqual(None, error)

    def test_json_value_validator_valid_sample_check(self):
        is_valid, error = json_value_validator(scenario="Passthrough", concurrency=100,
                                                message_size=1200,
                                                sample_count=10, type="sampling_check")
        self.assertEqual(True, is_valid)
        self.assertEqual(None, error)

    def test_json_value_validator_invalid_sample_counts(self):
        invalid_sample_counts = ["string", -1, 0, 5001, 100.1, {100}, [100], None]
        for sample_count in invalid_sample_counts:
            is_valid, error = json_value_validator(scenario="Passthrough", concurrency=100,
                                                    message_size=1200,
                                                    sample_count=sample_count ,type="sampling_check")
            self.assertEqual(False, is_valid)
            self.assertIsNotNone(error)

    def test_json_value_validator_invalid_scenario(self):
        invalid_scenario = ["string", 1, 1.1, True, {"Passthrough"}, ["Passthrough"], None]
        for scenario in invalid_scenario:
            is_valid, error = json_value_validator(scenario=scenario, concurrency=100,
                                                    message_size=1200)
            self.assertEqual(False, is_valid)
            self.assertIsNotNone(error)


    def test_json_value_validator_invalid_concurrencies(self):
        invalid_concurrencies = ["string", 0, -1, 0.1, 100.21, 1001, {100}, [100], None]
        for concurrency in invalid_concurrencies:
            is_valid, error = json_value_validator(scenario="Passthrough", concurrency=concurrency,
                                                    message_size=1200)
            self.assertEqual(False, is_valid)
            self.assertIsNotNone(error)

    def test_json_value_validator_invalid_message_sizes(self):
        invalid_message_sizes = ["string", 0, 102400.1, {100}, [100], None]
        for message_size in invalid_message_sizes:
            is_valid, error = json_value_validator(scenario="Passthrough", concurrency=100,
                                                    message_size=message_size)
            self.assertEqual(False, is_valid)
            self.assertIsNotNone(error)

    # Tests for Predictions
    @mock.patch('application.regressor.BayesianPolynomialRegressor.predict_gp', return_value=[1500])
    def test_max_tps_no_sampling(self, mock_check_output):
        tps, concurrency = get_regressor().max_tps(
            ["Passthrough", 10240],
            method=const.NO_SAMPLING,
        )
        self.assertEqual(1500, tps)
        self.assertEqual(1, concurrency)

    @mock.patch('application.regressor.BayesianPolynomialRegressor.predict', return_value=[[1500]])
    def test_max_tps_sampling(self, mock_check_output):
        tps, concurrency = get_regressor().max_tps(
            ["Passthrough", 10240],
            method=const.SAMPLING,
            sample_count=100
        )
        self.assertEqual(1500, tps)
        self.assertEqual(1, concurrency)


    @mock.patch('application.regressor.BayesianPolynomialRegressor.predict', return_value=[1500])
    def test_prediction_sampling(self, mock_check_output):
        tps = get_regressor().predict_point(
            ["Passthrough", 100, 10240],
            method=const.SAMPLING, sample_count=100)
        self.assertEqual(1500, tps)


    @mock.patch('application.regressor.BayesianPolynomialRegressor.predict_gp', return_value=[1500])
    def test_prediction_no_sampling(self, mock_check_output):
        tps = get_regressor().predict_point(
            ["Passthrough", 100, 10240],
            method=const.NO_SAMPLING)
        self.assertEqual(1500, tps)

    # Service Tests
    @mock.patch('application.regressor.BayesianPolynomialRegressor.predict_gp', return_value=[1500])
    def test_service_predict_performance_no_sampling(self, mock_check_output):
            mock_request_headers = {'content-type': 'application/json'}
            mock_request_data = {
                "scenario": "Transformation",
                "message_size": 1020,
                "concurrency": 234
            }
            client = ai_capacity_planner.test_client()
            url = '/predict_point'
            response = client.post(url, data=json.dumps(mock_request_data), headers=mock_request_headers)
            self.assertEqual(b'{"latency":156.0,"tps":1500}\n', response.get_data())

    @mock.patch('application.regressor.BayesianPolynomialRegressor.predict', return_value=[1500])
    def test_service_predict_performance_sampling(self, mock_check_output):
            mock_request_headers = {'content-type': 'application/json'}
            mock_request_data = {
                "scenario": "Transformation",
                "message_size": 1020,
                "concurrency": 234,
                "method": "sampling"
            }
            client = ai_capacity_planner.test_client()
            url = '/predict_point'
            response = client.post(url, data=json.dumps(mock_request_data), headers=mock_request_headers)
            self.assertEqual(b'{"latency":156.0,"tps":1500}\n', response.get_data())

    @mock.patch('application.regressor.BayesianPolynomialRegressor.predict', return_value=[[1500]])
    def test_service_predict_max_performance_sampling(self, mock_check_output):
            mock_request_headers = {'content-type': 'application/json'}
            mock_request_data = {
                "scenario": "Transformation",
                "message_size": 1020,
                "method": "sampling"
            }
            client = ai_capacity_planner.test_client()
            url = '/max_tps'
            response = client.post(url, data=json.dumps(mock_request_data), headers=mock_request_headers)
            self.assertEqual(b'{"concurrency":1,"latency":0.67,"max_tps":1500}\n', response.get_data())

    @mock.patch('application.regressor.BayesianPolynomialRegressor.predict_gp', return_value=[1500])
    def test_service_predict_max_performance_no_sampling(self, mock_check_output):
            mock_request_headers = {'content-type': 'application/json'}
            mock_request_data = {
                "scenario": "Transformation",
                "message_size": 1020,
            }
            client = ai_capacity_planner.test_client()
            url = '/max_tps'
            response = client.post(url, data=json.dumps(mock_request_data), headers=mock_request_headers)
            self.assertEqual(b'{"concurrency":1,"latency":0.67,"max_tps":1500}\n', response.get_data())


if __name__ == '__main__':
    unittest.main()
