import math
import numpy as np
import pandas as pd
import application.constants as const
import pymc3 as pm
from application.response_formatter import formatter


seed = 42
np.random.seed(42)

# Load the pickle once but create a new BayesianPolynomialRegressor to encompose 
# the model's content in each new instance of the class.
raw_model_ref = open(const.model_path, 'rb').read()
model = pickle.load(raw_model_ref)

class BayesianPolynomialRegressor:
    def __init__(self):
        self.poly_model = model["model"]
        self.trace = model["trace"]
        self.x_shared = model["x_shared"]
        self.f_pred = model["f_pred"]
        self.scaler = model["scaler"]
        self.encoder = model["encoder"]
        self.gp = model["gp"]


    def predict(self, sample_count=const.DEFAULT_SAMPLE_COUNT):
        with self.poly_model:
            pred_samples = pm.sample_posterior_predictive(self.trace, vars=[self.f_pred], samples=sample_count, random_seed=seed)
            y_pred, uncer = pred_samples["f_pred"].mean(axis=0), pred_samples["f_pred"].std(axis=0)
            print(y_pred)
            return y_pred

    def predict_gp(self):
        with self.poly_model:
            mu, var = self.gp.predict(Xnew=self.x_shared, point=self.trace[0], diag=True)
            print(mu)
            return mu

    def predict_list(self, method = None, sample_count=const.DEFAULT_SAMPLE_COUNT, file_name="custom.csv"):
        dataset = pd.read_csv(const.data_path+file_name);

        x_custom = dataset.iloc[:, [0, 1, 2]].values;
        x_custom[:, 0] = self.encoder.transform(x_custom[:, 0]);
        x_custom = self.scaler.transform(x_custom);

        self.x_shared.set_value(x_custom)

        if method == "NS":
            self.predict_gp()
        else:
            self.predict(sample_count=sample_count)

    def predict_point(self, data, method = None, sample_count=const.DEFAULT_SAMPLE_COUNT):

        x_val = data;

        x_val[0] = self.encoder.transform([x_val[0]])[0]
        x_val = self.scaler.transform([x_val])

        self.x_shared.set_value(x_val)

        if method == "NS":
            prediction = self.predict_gp()
            formatter(prediction[0])
            return prediction[0]
        else:
            prediction = self.predict(sample_count=sample_count)
            return prediction


    def max_tps(self, data, method = None, sample_count=2000):
        print("In Max TPS")
        my_list = []
        scenario = data[0];
        message_size = data[1];

        for concurrency in range(50, 1000, 10):
            my_list.append([scenario, concurrency, message_size])

        data_array = np.array(my_list)
        data_array[:, 0] = self.encoder.transform(data_array[:, 0]);
        data_array = self.scaler.transform(data_array);

        self.x_shared.set_value(data_array)

        if method == "NS":
            predictions = self.predict_gp()
            return max(predictions)

        else:
            predictions = self.predict(sample_count=sample_count)
            return max(predictions)

