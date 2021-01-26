#!/bin/bash

set -e
# Copyright (c) 2021, WSO2 Inc. (http://www.wso2.com). All Rights Reserved.
#
#  This software is the property of WSO2 Inc. and its suppliers, if any.
#  Dissemination of any information or reproduction of any material contained
#  herein is strictly forbidden, unless permitted by WSO2 in accordance with
#  the WSO2 Commercial License available at http://wso2.com/licenses.
#  For specific language governing the permissions and limitations under
#  this license, please see the license as well as any agreement you’ve
#  entered into with WSO2 governing the purchase of this software and any

###
# This script generates dvc metadata files from a properties file containing hashes. It has been written to be used
# for the Capacity Planner initContainer on Choreo
#
# Inputs: model properties file having the following format
# BAYESIAN_POLYNOMIAL_MD5=
#
# Outputs: dvc metadata files
###

if [ $# -eq 0 ]
then
  echo "[ERROR] - No arguments supplied. Please supply the model properties file as an argument"
  exit 1
fi

if [ ! -f $1 ]
then
  echo "[ERROR] - model properties File Not Found"
  exit 1
fi

MODEL_PROPERTIES_FILE=$1

declare -a md5Arr
declare -a dvcMetadataFilenames=("bayesian_regressor.p")

md5Arr[0]=`grep "BAYESIAN_POLYNOMIAL_MD5" $MODEL_PROPERTIES_FILE | cut -d'=' -f2`

for i in {0..0}
do
	## Make sure this block is indented with a tab and not with spaces. If the latter is used, it results in a
	## syntax error due to the use of heredoc
  cat <<-EOF > model/${dvcMetadataFilenames[i]}.dvc
	outs:
	- md5: ${md5Arr[i]}
	  path: ${dvcMetadataFilenames[i]}
	EOF
done