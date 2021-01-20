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

import sys
from os.path import dirname
from wsgi import app as ai_capacity_planner
from flask import request, jsonify, Response
from application.regressor import BayesianPolynomialRegressor
from pymc3 import memoize
import application.constants as const
from application.response_formatter import formatter, json_value_validator
from application.logging_handler import logger

@ai_capacity_planner.route('/')
def check():
    """
    Check availability of service.
    :return HTTP 200 Response:
    """
    return Response(status=const.HTTP_200_OK)

@ai_capacity_planner.route('/predict_point', methods=['POST'])
def point_prediction():
    """
    Return Latency and TPS for a given scenario, message size and concurrency
    :return TPS and Little's law Latency with HTTP 200:
    """
    if request.method == "POST":
        data = request.get_json()
        method = const.DEFAULT_METHOD
        sample_count = const.DEFAULT_SAMPLE_COUNT

        try:
            scenario = data[const.SCENARIO].capitalize();
            concurrency = data[const.CONCURRENCY]
            message_size = data[const.MESSAGE_SIZE]
            if not (json_value_validator(scenario=scenario,concurrency=concurrency,message_size=message_size, type="point_pred")):
                logger.error("Invalid values in JSON request: constraint violation: point_pred")
                return Response(status=const.HTTP_405_METHOD_NOT_ALLOWED)
        except Exception as e:
            logger.exception("Invalid JSON Format: point_pred");
            return Response(status=const.HTTP_422_UNPROCESSABLE_ENTITY)

        if const.METHOD in data:
            if data[const.METHOD] == const.SAMPLING:
                method = const.SAMPLING
                try:
                    if not (data.get(const.SAMPLE_COUNT) is None):
                        sample_count = data[const.SAMPLE_COUNT]
                        if not (json_value_validator(sample_count=sample_count, type="sampling_check")):
                            logger.error("Invalid values in JSON request: constraint violation for sample_count: point_pred")
                            return Response(status=const.HTTP_405_METHOD_NOT_ALLOWED)
                except Exception as e:
                    logger.exception("Invalid JSON Format: point_pred");
                    return Response(status=const.HTTP_422_UNPROCESSABLE_ENTITY)

        try:
            poly_regressor = BayesianPolynomialRegressor()
            prediction = poly_regressor.predict_point([scenario, concurrency, message_size], method=method, sample_count=sample_count);
            tps,latency = formatter(tps=prediction, concurrency=concurrency);

            #Clear PyMC3 cache
            memoize.clear_cache()

            return jsonify(
                tps=tps,
                latency=latency
            )

        except Exception as e:
            logger.exception("ML Model Error : point_pred")
            return Response(status=const.HTTP_500_INTERNAL_SERVER_ERROR)

@ai_capacity_planner.route('/max_tps', methods=['POST'])
def max_tps_prediction():
    """
    Return Maximum TPS for a given scenario and message size
    :return Max TPS with HTTP 200:
    """
    if request.method == "POST":
        data = request.get_json()
        method = const.DEFAULT_METHOD
        sample_count = const.DEFAULT_SAMPLE_COUNT

        try:
            scenario = data[const.SCENARIO].capitalize();
            message_size = data[const.MESSAGE_SIZE]
            if not (json_value_validator(scenario=scenario,message_size=message_size, type="max_tps")):
                logger.error("Invalid values in JSON request: constraint violation: max_tps")
                return Response(status=const.HTTP_405_METHOD_NOT_ALLOWED)
        except Exception as e:
            logger.exception("Invalid JSON Format: max_tps");
            return Response(status=const.HTTP_422_UNPROCESSABLE_ENTITY)

        if const.METHOD in data:
            if data[const.METHOD] == const.SAMPLING:
                method = const.SAMPLING
                try:
                    if not (data.get(const.SAMPLE_COUNT) is None):
                        sample_count = data[const.SAMPLE_COUNT]
                        if not (json_value_validator(sample_count=sample_count, type="sampling_check")):
                            logger.error("Invalid values in JSON request: constraint violation: max_tps : sample_count")
                            return Response(status=const.HTTP_405_METHOD_NOT_ALLOWED)
                except Exception as e:
                    logger.exception("Invalid JSON Format: point_pred");
                    return Response(status=const.HTTP_422_UNPROCESSABLE_ENTITY)

        try:
            poly_regressor = BayesianPolynomialRegressor()
            tps = poly_regressor.max_tps([scenario, message_size], method=method, sample_count=sample_count)
            tps = formatter(tps=tps);

            #Clear PyMC3 Cache
            memoize.clear_cache()

            return jsonify(
                max_tps=tps,
            )

        except Exception as e:
            logger.exception("ML Model Error : max_tps")
            return Response(status=const.HTTP_500_INTERNAL_SERVER_ERROR)