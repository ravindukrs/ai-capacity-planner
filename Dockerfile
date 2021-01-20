# Copyright (c) 2021, WSO2 Inc. (http://www.wso2.com). All Rights Reserved.
#  This software is the property of WSO2 Inc. and its suppliers, if any.
#  Dissemination of any information or reproduction of any material contained
#  herein is strictly forbidden, unless permitted by WSO2 in accordance with
#  the WSO2 Commercial License available at http://wso2.com/licenses.
#  For specific language governing the permissions and limitations under
#  this license, please see the license as well as any agreement you’ve
#  entered into with WSO2 governing the purchase of this software and any

FROM ubuntu:20.04

WORKDIR /app

COPY . /app

RUN apt-get update && \
    apt-get install -y --no-install-recommends python3.8=3.8.5-1~20.04\
      python3-pip=20.0.2-5ubuntu1.1 \
      python3-venv=3.8.2-0ubuntu2 && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

RUN pip3 --no-cache-dir install -r requirements.txt

EXPOSE 5000

CMD ["gunicorn" , "-w", "3", "--bind", "0.0.0.0:5000", "application.capacity_planner_service:ai_capacity_planner", "--timeout", "120"]


