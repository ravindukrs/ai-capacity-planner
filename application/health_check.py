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

from application.regressor import get_regressor
import application.constants as const
from flask import Response
import time
from application.logging_handler import logger


HEALTH_CHECK_INTERVAL = 30  # in seconds
LAST_CHECK_TIME = None
LAST_CHECK_RESPONSE = None


def run_health_check():
    """
    Performs a self test of the capacity planner service by comparing the predicted output with the
    expected output for a given request
    :return: HTTP response
    """
    global LAST_CHECK_RESPONSE
    global LAST_CHECK_TIME

    current_time = int(time.time())

    if (LAST_CHECK_TIME is None or current_time - LAST_CHECK_TIME >= HEALTH_CHECK_INTERVAL):
        try:
            expected_tps = 2482.337454686785
            returned_tps = get_regressor().predict_point(
                            ["Passthrough", 100, 10240],
                            method=const.NO_SAMPLING)

            if round(expected_tps, 2) == round(returned_tps, 2):
                # Rounding TPS to account for changes with different C compilers
                LAST_CHECK_RESPONSE = Response(status=const.HTTP_200_OK)
            else:
                logger.info("ML model prediction in health check does not match")
                LAST_CHECK_RESPONSE = Response(status=const.HTTP_503_SERVICE_UNAVAILABLE)
        except Exception:
            logger.exception("Exception in Capacity Planner health check: ")
            LAST_CHECK_RESPONSE = Response(status=const.HTTP_500_INTERNAL_SERVER_ERROR)
        LAST_CHECK_TIME = current_time
    return LAST_CHECK_RESPONSE
