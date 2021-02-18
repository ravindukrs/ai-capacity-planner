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

from application.wsgi import app as ai_capacity_planner
from flask import request, jsonify, Response
from pymc3 import memoize
import application.constants as const
from application.response_formatter import formatter, json_value_validator
from application.logging_handler import logger
from application.regressor import get_regressor
from application.health_check import run_health_check

@ai_capacity_planner.route('/liveness', methods=['GET'])
def liveness():
    """
    Check availability of service.
    :return HTTP 200 Response:
    """
    return run_health_check()

@ai_capacity_planner.route('/readiness', methods=['GET'])
def readiness():
    """
    Check readiness of service.
    :return HTTP 200 Response:
    """
    return run_health_check()

@ai_capacity_planner.route('/ping', methods=['GET'])
def ping_check():
    """
    Check reachability of service.
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
        method = const.DEFAULT_METHOD
        sample_count = const.DEFAULT_SAMPLE_COUNT
        data = request.get_json()

        if data is None:
            logger.error("Payload is missing.")
            return jsonify({"error": "Payload is missing"}), \
                const.HTTP_400_BAD_REQUEST

        try:
            scenario = data.get(const.SCENARIO)
            concurrency = data.get(const.CONCURRENCY)
            message_size = data.get(const.MESSAGE_SIZE)

            is_valid, error = json_value_validator(
                scenario=scenario, concurrency=concurrency,
                message_size=message_size, type="point_pred"
            )
            if not is_valid:
                logger.error("Invalid values in JSON request: "
                             "constraint violation: point_pred: "+error)
                return jsonify({"error": "Invalid Request: "+error}), \
                    const.HTTP_422_UNPROCESSABLE_ENTITY
        except Exception as e:
            logger.exception("Uncaught exception occurred "
                             "in request validation: ", e)
            return jsonify({"error": "Uncaught exception occurred in request "
                            "validation"}), const.HTTP_422_UNPROCESSABLE_ENTITY

        if const.METHOD in data:
            if data[const.METHOD] == const.SAMPLING:
                method = const.SAMPLING
                try:
                    if not (data.get(const.SAMPLE_COUNT) is None):
                        sample_count = data[const.SAMPLE_COUNT]
                        is_valid, error = json_value_validator(
                            sample_count=sample_count, type="sampling_check"
                        )
                        if not is_valid:
                            logger.error("Invalid values in JSON request: "
                                         "constraint violation for "
                                         "sample_count: point_pred "+error)
                            return jsonify({
                                "error": "Invalid Request: "+error
                            }), \
                                const.HTTP_422_UNPROCESSABLE_ENTITY
                except Exception as e:
                    logger.exception("Uncaught exception occurred "
                                     "in request validation block: ", e)
                    return jsonify({"error": "Uncaught exception "
                                    "occurred in request validation"}), \
                        const.HTTP_422_UNPROCESSABLE_ENTITY

        try:
            prediction = get_regressor().predict_point(
                [scenario.capitalize(), concurrency, message_size],
                method=method, sample_count=sample_count)
            tps, latency = formatter(tps=prediction, concurrency=concurrency)

            # Clear PyMC3 cache
            memoize.clear_cache()

            return jsonify(
                tps=tps,
                latency=latency
            )

        except Exception as e:
            logger.exception("ML Model Error : point_pred: ", e)
            return jsonify({"error": "Error during prediction "
                            "or post processing"}), \
                const.HTTP_500_INTERNAL_SERVER_ERROR

    else:
        return Response(status=const.HTTP_405_METHOD_NOT_ALLOWED)


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

        if data is None:
            logger.error("Payload is missing.")
            return jsonify({"error": "Payload is missing"}),\
                const.HTTP_400_BAD_REQUEST

        try:
            scenario = data.get(const.SCENARIO)
            message_size = data.get(const.MESSAGE_SIZE)

            is_valid, error = json_value_validator(
                scenario=scenario, message_size=message_size, type="max_tps"
            )
            if not is_valid:
                logger.error("Invalid values in JSON request: "
                             "constraint violation: max_tps: "+error)
                return jsonify({"error": "Invalid Request: "+error}), \
                    const.HTTP_422_UNPROCESSABLE_ENTITY
        except Exception as e:
            logger.exception("Uncaught exception occurred in request "
                             "validation block:", e)
            return jsonify({"error": "Uncaught exception occurred "
                            "in request validation"}), \
                const.HTTP_422_UNPROCESSABLE_ENTITY

        if const.METHOD in data:
            if data[const.METHOD] == const.SAMPLING:
                method = const.SAMPLING
                try:
                    if not (data.get(const.SAMPLE_COUNT) is None):
                        sample_count = data[const.SAMPLE_COUNT]
                        is_valid, error = json_value_validator(
                            sample_count=sample_count, type="sampling_check"
                        )
                        if not is_valid:
                            logger.error("Invalid values in JSON request: "
                                         "constraint violation: max_tps : "
                                         "sample_count")
                            return jsonify({
                                "error": "Invalid Request: "+error
                            }), \
                                const.HTTP_422_UNPROCESSABLE_ENTITY
                except Exception as e:
                    logger.exception("Uncaught exception occurred "
                                     "in request validation block:", e)
                    return Response(status=const.HTTP_422_UNPROCESSABLE_ENTITY)

        try:
            tps, concurrency = get_regressor().max_tps(
                [scenario.capitalize(), message_size],
                method=method,
                sample_count=sample_count
            )
            tps, latency = formatter(tps=tps, concurrency=int(concurrency))

            # Clear PyMC3 Cache
            memoize.clear_cache()

            return jsonify(
                max_tps=tps,
                latency=latency,
                concurrency=int(concurrency)
            )

        except Exception as e:
            logger.exception("ML Model Error : max_tps: ", e)
            return jsonify({"error": "Error during prediction "
                            "or post processing"}), \
                const.HTTP_500_INTERNAL_SERVER_ERROR

    else:
        return Response(status=const.HTTP_405_METHOD_NOT_ALLOWED)
