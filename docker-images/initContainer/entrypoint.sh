#!/bin/bash

set -e
#"""
# Copyright (c) 2021, WSO2 Inc. (http://www.wso2.com). All Rights Reserved.
#  This software is the property of WSO2 Inc. and its suppliers, if any.
#  Dissemination of any information or reproduction of any material contained
#  herein is strictly forbidden, unless permitted by WSO2 in accordance with
#  the WSO2 Commercial License available at http://wso2.com/licenses.
#  For specific language governing the permissions and limitations under
#  this license, please see the license as well as any agreement you’ve
#  entered into with WSO2 governing the purchase of this software and any
#"""


echo "Starting Init Container"
# This path comes with CSI secret store
MODEL_CONNECTION_STRING="$(cat /mnt/csi/secret-capacity-planner/MODEL-CONNECTION-STRING)"
bash generate_dvc_metadata.sh models.properties
dvc remote add -d -f --local storageremote azure://modelcontainer
dvc remote modify --local storageremote connection_string "$MODEL_CONNECTION_STRING"
dvc pull
dvc remote remove --local storageremote
