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
import numbers
from application.logging_handler import logger


def formatter(tps, concurrency=None):
    """
    Get predicted TPS and format the TPS.
    If concurrency is available, calculate Little's Law latency
    :param data: Concurrency and Message Size
    :return TPS(max tps) or TPS and Little's law Latency:
    """
    # Round up TPS
    tps = math.ceil(tps * 100.0) / 100.0
    if tps < 1:
        tps = 1

    # Calcuate Latency
    if not isinstance(concurrency, numbers.Number):
        return tps
    else:
        # Calculate Latency with Little's Law
        latency = concurrency / tps * 1000
        latency = round(latency, 2)
        return tps, latency


def json_value_validator(scenario=None, concurrency=None,
                         message_size=None, sample_count=None,
                         type="point_pred"):
    """
    Validate the JSON input.
    :param scenario: 'Passthrough' or 'Transformation'
    :param concurrency: Concurrency
    :param message_size: Message Size
    :param sample_count: Sample Count for Sampling Method
    :param type: point_pred or max_tps
    :return is_valid: Validity of JSON:
    """
    is_valid = True

    if type == "point_pred" or type == "max_tps":
        if not isinstance(scenario, str):
            error = "Scenario is undefined or not a String"
            logger.error(error)
            return False, error

        if scenario.capitalize() != "Passthrough" \
                and scenario.capitalize() != "Transformation":
            error = "Scenario defined is not valid. Expected " \
                    "'Transformation' or 'Passthrough'"
            logger.error(error)
            return False, error

        if not isinstance(message_size, numbers.Number):
            error = "Message Size undefined or not a number"
            logger.error(error)
            return False, error

        if message_size < 1 or message_size > 102400:
            error = "Message size is not in range. " \
                    "Supported range 1 - 102400"
            logger.error(error)
            return False, error

    if type == "point_pred":
        if not isinstance(concurrency, numbers.Number):
            error = "Concurrency is undefined or not a number. " \
                    "Expected an Integer"
            logger.error(error)
            return False, error

        if not isinstance(concurrency, int):
            error = "Concurrency is not an integer. " \
                    "Expected an integer."
            logger.error(error)
            return False, error

        if concurrency < 1 or concurrency > 1000:
            error = "Message size is not in range. " \
                    "Supported range 1 - 1000"
            logger.error(error)
            return False, error

    if type == "sampling_check":
        if not isinstance(sample_count, numbers.Number):
            error = "Sample Count is not an integer. " \
                    "Expected an integer."
            logger.error(error)
            return False, error

        if not isinstance(sample_count, int):
            error = "Sample Count is not an integer. " \
                    "Expected an integer."
            logger.error(error)
            return False, error

        if not sample_count >= 1:
            error = "Sample Count is not in range. " \
                    "Supported range 1 - 5000"
            logger.error(error)
            return False, error

        if not sample_count <= 5000:
            error = "Sample Count is not in range. " \
                    "Supported range 1 - 5000"
            logger.error(error)
            return False, error

    return is_valid, None
