# Copyright (c) 2021, WSO2 Inc. (http://www.wso2.com). All Rights Reserved.
#
#  This software is the property of WSO2 Inc. and its suppliers, if any.
#  Dissemination of any information or reproduction of any material contained
#  herein is strictly forbidden, unless permitted by WSO2 in accordance with
#  the WSO2 Commercial License available at http://wso2.com/licenses.
#  For specific language governing the permissions and limitations under
#  this license, please see the license as well as any agreement you’ve
#  entered into with WSO2 governing the purchase of this software and any

FROM ubuntu:20.04 AS builder

RUN apt-get update && \

    apt-get install -y --no-install-recommends python3.8=3.8.5-1~20.04\
      python3-pip=20.0.2-5ubuntu1.1 \
      python3-venv=3.8.2-0ubuntu2 && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

RUN python3 -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

COPY docker-images/service/requirements.txt .

RUN pip3 --no-cache-dir install wheel==0.36.1 && \
    pip3 --no-cache-dir install -r requirements.txt  # building wheel for modules fail if wheel is not
                                                     # already installed. Hence the reason to execute a separate pip3
                                                     # install for wheel before installing requirements

FROM ubuntu:20.04

ARG GROUP=ai
ARG USER=python-ai

RUN groupadd --system --gid 500 ${GROUP} && \
    useradd --system --create-home --home-dir /home/${USER} --no-log-init --gid 500 --uid 500 ${USER} && \
    apt-get update && \

    apt-get install -y --no-install-recommends libgomp1=10.2.0-5ubuntu1~20.04 \
      python3.8=3.8.5-1~20.04 \
      python3-venv=3.8.2-0ubuntu2 && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /home/${USER}/choreo-ai-capacity-planner

COPY --from=builder --chown=${USER}:${GROUP} /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# sources
COPY --chown=${USER}:${GROUP} application/ application/

# run script
COPY --chown=${USER}:${GROUP} docker-images/service/entrypoint.sh .

USER ${USER}

EXPOSE 5000

ENTRYPOINT ["/bin/bash","entrypoint.sh"]
