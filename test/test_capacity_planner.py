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
from application.regressor import get_regressor
import application.constants as const

class TestCapacityPlanner(unittest.TestCase):
    def test_max_tps_no_sampling(self):
        tps, concurrency = get_regressor().max_tps(
            ["Passthrough", 10240],
            method=const.NO_SAMPLING,
        )
        self.assertEqual(2482.6010321806693, tps)
        self.assertEqual(60, concurrency)

    def test_max_tps_sampling(self):
        tps, concurrency = get_regressor().max_tps(
            ["Passthrough", 10240],
            method=const.SAMPLING,
            sample_count=100
        )
        self.assertEqual(2499.7054760374053, tps)
        self.assertEqual(20, concurrency)

    def test_prediction_sampling(self):
        tps = get_regressor().predict_point(
            ["Passthrough", 100, 10240],
            method=const.SAMPLING, sample_count=100)
        self.assertEqual(2469.6123184650064, tps)

    def test_prediction_no_sampling(self):
        tps = get_regressor().predict_point(
            ["Passthrough", 100, 10240],
            method=const.NO_SAMPLING)
        self.assertEqual(2482.337454686785, tps)


if __name__ == '__main__':
    unittest.main()
