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

FROM ubuntu:20.04

ARG GROUP=ai
ARG USER=python-ai

RUN groupadd --system --gid 500 ${GROUP} && \
    useradd --system --create-home --home-dir /home/${USER} --no-log-init --gid 500 --uid 500 ${USER} && \
    apt update && \
    apt install -y git wget && \
    wget https://dvc.org/deb/dvc.list -O /etc/apt/sources.list.d/dvc.list && \
    apt update && \
    apt install -y dvc && \
    apt purge -y wget && \
    apt autoremove -y && \
    apt clean && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /home/${USER}/choreo-ai-capacity-planner

COPY --chown=${USER}:${GROUP} model/ model/
COPY --chown=${USER}:${GROUP} .dvc/ .dvc/
COPY --chown=${USER}:${GROUP} .git/ .git/
COPY --chown=${USER}:${GROUP} docker-images/initContainer/generate_dvc_metadata.sh .
COPY --chown=${USER}:${GROUP} docker-images/initContainer/entrypoint.sh .

USER ${USER}

ENTRYPOINT ["/bin/bash","entrypoint.sh"]