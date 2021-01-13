import pickle
import application.constants as const
from application.logging_handler import logger

def load_model():
    """
    Load Pickle Model.
    :return Record with model params:
    """
    try:
        logger.info("Loading Model")
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
    except Exception as e:
        logger.exception("Model Load Failed");


model = load_model();

def get_model():
    """
    Return Model parameters.
    :return model:
    """
    return model

