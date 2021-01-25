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

#Model
model_path = "model/bayesian_regressor.p"

#Datasets
training_data = "dataset/dataset.csv"
data_path = "dataset/"

#Results
result_path = "results/"

# HTTP response codes
HTTP_200_OK = 200
HTTP_500_INTERNAL_SERVER_ERROR = 500
HTTP_503_SERVICE_UNAVAILABLE = 503
HTTP_400_BAD_REQUEST = 400
HTTP_405_METHOD_NOT_ALLOWED = 405
HTTP_422_UNPROCESSABLE_ENTITY = 422

#Regressor Properties
DEFAULT_SAMPLE_COUNT=2000

#JSON KEYS
SAMPLE_COUNT="sample_count"
CONCURRENCY = "concurrency"
MESSAGE_SIZE = "message_size"
METHOD = "method"
SCENARIO = "scenario"
SAMPLING = "sampling"
NO_SAMPLING = "NS"
DEFAULT_METHOD = NO_SAMPLING