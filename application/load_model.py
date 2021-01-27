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

import pickle
import application.constants as const
from application.logging_handler import logger
from os import path


def load_model():
    """
    Load Pickle Model.
    :return Record with model params:
    """

    try:
        logger.info("Loading Model")
        if path.exists(const.model_path):
            with open(const.model_path, 'rb') as buff:
                data = pickle.load(buff)
                logger.info("Model Loaded")
                return {
                    "model": data['model'],
                    "trace": data['trace'],
                    "x_shared": data['X_New_shared'],
                    "f_pred": data['f_pred'],
                    "scaler": data['scaler'],
                    "encoder": data['encoder'],
                    "gp": data['gp'],
                }
        else:
            logger.exception("Model path does not exist")
            return None
    except Exception as e:
        logger.exception("Model Load Failed: ", e)


def get_model():
    """
    Return Model parameters.
    :return model:
    """
    model = load_model()
    if model is not None:
        return model
    else:
        logger.exception("Cannot load model")
        logger.info("Exiting Application")
        exit(1)
