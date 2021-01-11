import sys
from os.path import dirname
sys.path.append(dirname("."))
from flask import Flask
from flask import request, jsonify, Response
from application.regressor import BayesianPolynomialRegressor
from pymc3 import memoize
import application.constants as const
from application.response_formatter import formatter, json_value_validator
from application.logging_handler import logger


ai_capacity_planner = Flask(__name__)

@ai_capacity_planner.route('/')
def check():
    return Response(status=const.HTTP_200_OK)

@ai_capacity_planner.route('/predict_point', methods=['POST'])
def point_prediction():

    if request.method == "POST":
        data = request.get_json()
        method = const.DEFAULT_METHOD
        sample_count = const.DEFAULT_SAMPLE_COUNT

        try:
            scenario = data['scenario'].capitalize();
            concurrency = data['concurrency']
            message_size = data['message_size']
            if not (json_value_validator(scenario=scenario,concurrency=concurrency,message_size=message_size, type="point_pred")):
                logger.error("Invalid values in JSON request: constraint violation: point_pred")
                return Response(status=const.HTTP_405_METHOD_NOT_ALLOWED)
        except Exception as e:
            logger.exception("Invalid JSON Format: point_pred");
            return Response(status=const.HTTP_422_UNPROCESSABLE_ENTITY)

        if "method" in data:
            if data['method'] == "sampling":
                method = "sampling"
                try:
                    if not (data.get('sample_count') is None):
                        sample_count = data['sample_count']
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
    if request.method == "POST":
        data = request.get_json()
        method = const.DEFAULT_METHOD
        sample_count = const.DEFAULT_SAMPLE_COUNT

        try:
            scenario = data['scenario'].capitalize();
            message_size = data['message_size']
            if not (json_value_validator(scenario=scenario,message_size=message_size, type="max_tps")):
                logger.error("Invalid values in JSON request: constraint violation: max_tps")
                return Response(status=const.HTTP_405_METHOD_NOT_ALLOWED)
        except Exception as e:
            logger.exception("Invalid JSON Format: max_tps");
            return Response(status=const.HTTP_422_UNPROCESSABLE_ENTITY)

        if "method" in data:
            if data['method'] == "sampling":
                method = "sampling"
                try:
                    if not (data.get('sample_count') is None):
                        sample_count = data['sample_count']
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

            memoize.clear_cache()
            return jsonify(
                max_tps=tps,
            )

        except Exception as e:
            logger.exception("ML Model Error : max_tps")
            return Response(status=const.HTTP_500_INTERNAL_SERVER_ERROR)

if __name__ == '__main__':
    ai_capacity_planner.run(threaded=True, host='0.0.0.0', port=5000)
