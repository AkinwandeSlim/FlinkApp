from flask import Flask, jsonify, request
from river import linear_model
from river import metrics
from river import evaluate
from river import preprocessing
from river import compose
import pandas as pd
import json
#from beta_distribution_drift_detector.concept import Concept
from beta_distribution_drift_detector.bdddc import BDDDC

import pandas as pd
import numpy as np
# from sklearn.model_selection import train_test_split
# import lightgbm as lgb


app = Flask(__name__)
port=9000
class RiverML:
    # fraud detection model
    model = compose.Pipeline(
        preprocessing.StandardScaler(),
        linear_model.LogisticRegression()
    )

    # ROCAUC metric to score the model as it trains
    metric = metrics.ROCAUC()
    
    drift_detector = BDDDC()

    
    # Counter for number of instances processed
    instance_counter = 0
    
fraud_model = RiverML()    
@app.route('/predict', methods=['POST'])
def predict():
    
    data = request.get_json()
    df = pd.DataFrame(data)
    
    # convert into dict
    x_data = df[['attrib1', 'attrib2', 'attrib3']].to_dict(orient='records')
    y_data = df['label'].tolist()  # convert to list
    
    
    
    # Check for concept drift
    fraud_model.instance_counter += len(x_data)   
    
    # do the prediction and score it
    y_preds = [fraud_model.model.predict_one(x) for x in x_data]
    y_pred = sum(y_preds) / len(y_preds)
    metric = fraud_model.metric.update(y_data, y_pred)

#     try:
#         fraud_model.drift_detector.add_element(np.array(y_preds, ndmin = 1), np.array(y_data, ndmin = 1))
#     except:
#         #print(e)
#         pass
    
#     if fraud_model.drift_detector.detected_change():
#         fraud_model.model = compose.Pipeline(
#             preprocessing.StandardScaler(),
#             linear_model.LogisticRegression()
#         )
        
#         for xi, yi in zip(x_data, y_data):
#             fraud_model.model.learn_one(xi, yi)
#         fraud_model.drift_detector = BDDDC()
#         fraud_model.instance_counter = 0
        
        
        
    for xi, yi in zip(x_data, y_data):
        fraud_model.model.learn_one(xi, yi)   
    
    return jsonify({'result': y_pred, 'performance': {'ROCAUC': fraud_model.metric.get()}})
    
    
if __name__ == '__main__':
    app.run(host="0.0.0.0", port=port)

    
        
    
    

# from flask import Flask, jsonify, request
# from river import linear_model
# from river import metrics
# from river import evaluate
# from river import preprocessing
# from river import compose
# import pandas as pd
# import json    
# import lightgbm as lgb
# from river import compose
# from river import tree
# from river import optim
# from lightgbm import LGBMClassifier
# import pickle
# import os
# app = Flask(__name__)
# port=9000


# class RiverML:
#     model_path = "/app/lgb_model.pkl"
#     # fraud detection model
#     model = compose.Pipeline(
#         preprocessing.StandardScaler(),
#         linear_model.LogisticRegression()
#     )

#     metric = {
#         "accuracy": metrics.Accuracy(),
#         "precision": lambda y_true, y_pred: metrics.Precision()(y_pred, y_true),
#         "recall": lambda y_true, y_pred: metrics.Recall()(y_pred, y_true),
#         "f1_score": lambda y_true, y_pred: metrics.F1()(y_pred, y_true),
#     }


#     @staticmethod
#     def initialise():
#         # Load the model from disk
# #         model_path = os.path.join(os.getcwd(), "lgb_model.pkl")
#         model_path = "/app/lgb_model.pkl"
#         try:
#             with open(model_path, "rb") as f:
#                 RiverML.model = pickle.load(f)
#         except FileNotFoundError:
#             print(f"{model_path} not found. Initializing with default model...")


#     @staticmethod
#     def save():
#         model_path = "/app/lgb_model.pkl"
#         with open(model_path, "wb") as f:
#             pickle.dump(RiverML.model, f)

# fraud_model = RiverML()
# fraud_model.initialise()
# @app.route('/predict', methods=['POST'])
# def predict():
#     data = request.get_json()
#     df = pd.DataFrame(data)
    
#     # convert into dict
#     x_data = df[['attrib1', 'attrib2', 'attrib3']].to_dict(orient='records')
#     y_data = df['label'].tolist()  # convert to list
    
#     # get window start and end times
#     window_start = df['window_start'].iloc[0]
#     window_end = df['window_end'].iloc[0]
    
#     # do the prediction and score it
#     y_pred = [fraud_model.model.predict_one(x) for x in x_data]
    
#     for i, (x, y) in enumerate(zip(x_data, y_data)):
#         y_pred = fraud_model.model.predict_one(x)
#         fraud_model.metric["accuracy"].update(y, y_pred)
#         fraud_model.metric["precision"].update(y, y_pred)
#         fraud_model.metric["recall"].update(y, y_pred)
#         fraud_model.metric["f1_score"].update(y, y_pred)
        
#     # calculate accuracy, precision, recall, and f1_score
#     accuracy = fraud_model.metric["accuracy"]
#     precision = fraud_model.metric["precision"]
#     recall = fraud_model.metric["recall"]
#     f1_score = fraud_model.metric["f1_score"]
    
#     # calculate throughput and latency
#     num_records = len(x_data)
#     elapsed_time = (window_end - window_start).total_seconds()
#     throughput = num_records / elapsed_time
#     latency = elapsed_time / num_records
    
#     # update the model
#     for x, y in zip(x_data, y_data):
#         fraud_model.model.learn_one(x, y)
    
#     return jsonify({'result': y_pred, 'accuracy': accuracy, 'precision': precision, 'recall': recall, 'f1_score': f1_score, 'throughput': throughput, 'latency': latency})

#     return jsonify({'result': y_pred, 'performance':fraud_model.metric.get()})

















# from flask import Flask, jsonify, request
# import pandas as pd
# import json
# import lightgbm as lgb
# from river import compose, optim, preprocessing, tree, metrics, evaluate
# from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
# from sklearn.pipeline import make_pipeline
# from sklearn.preprocessing import StandardScaler
# from river.experimental import LearnWithMiniBatch
# from joblib import dump, load

# app = Flask(__name__)
# port = 9000


# class RiverML:
#     model_path = "/app/lgb_model.joblib"

#     def __init__(self):
#         self.model = self.load_model()
#         self.metric = {
#             "accuracy": metrics.Accuracy(),
#             "precision": metrics.Precision(),
#             "recall": metrics.Recall(),
#             "f1_score": metrics.F1(),
#         }

#     def load_model(self):
#         try:
#             return load(self.model_path)
#         except FileNotFoundError:
#             print(f"{self.model_path} not found. Initializing with default model...")
#             return make_pipeline(StandardScaler(), LearnWithMiniBatch(tree.HoeffdingTreeClassifier()))

#     def save_model(self):
#         dump(self.model, self.model_path)

# fraud_model = RiverML()

# @app.route('/predict', methods=['POST'])
# def predict():
#     data = request.get_json()
#     df = pd.DataFrame(data)

#     # convert into dict
#     x_data = df[['attrib1', 'attrib2', 'attrib3']].to_dict(orient='records')
#     y_data = df['label'].tolist()  # convert to list

#     # get window start and end times
#     window_start = df['window_start'].iloc[0]
#     window_end = df['window_end'].iloc[0]

#     # do the prediction and score it
#     y_pred = [fraud_model.model.predict(x)[0] for x in x_data]

#     for i, (x, y) in enumerate(zip(x_data, y_data)):
#         fraud_model.model.learn_one(x, y)
#         for m in fraud_model.metric.values():
#             m.update(y, y_pred[i])

#     # calculate accuracy, precision, recall, and f1_score
#     accuracy = accuracy_score(y_data, y_pred)
#     precision = precision_score(y_data, y_pred, average="weighted")
#     recall = recall_score(y_data, y_pred, average="weighted")
#     f1 = f1_score(y_data, y_pred, average="weighted")

#     # calculate throughput and latency
#     num_records = len(x_data)
#     elapsed_time = (window_end - window_start).total_seconds()
#     throughput = num_records / elapsed_time
#     latency = elapsed_time / num_records

#     # save the model
#     fraud_model.save_model()

#     return jsonify({'result': y_pred, 'accuracy': accuracy, 'precision': precision, 'recall': recall, 'f1_score': f1, 'throughput': throughput, 'latency': latency})
















# from flask import Flask, jsonify, request
# import pandas as pd
# import json    
# import lightgbm as lgb
# from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score

# app = Flask(__name__)
# port=9000

# class LightGBMModel:
#     model_path = "/app/lightgbm_model.pkl"
#     model = LGBMClassifier()

#     def __init__(self):
#         self.model = lgb.LGBMClassifier()
#         self.initialise()

#     @staticmethod
#     def initialise():
#         # Load the model from disk
#         try:
#             with open(LightGBMModel.model_path, "rb") as f:
#                 LightGBMModel.model = pickle.load(f)
#         except FileNotFoundError:
#             print(f"{LightGBMModel.model_path} not found. Initializing with default model...")

#     @staticmethod
#     def save():
#         with open(LightGBMModel.model_path, "wb") as f:
#             pickle.dump(LightGBMModel.model, f)

#     @staticmethod
#     def fit_model(X, y):
#         LightGBMModel.model.fit(X=X, y=y)

#     @staticmethod
#     def predict_model(X):
#         y_pred = LightGBMModel.model.predict(X)
#         return y_pred.tolist()
    
#     @staticmethod
#     def update(df):
#         # preprocess the data
#         X = df[['attrib1', 'attrib2', 'attrib3']]
# #         X = pd.get_dummies(X, columns=['attrib1']) # assuming attrib1 is categorical
#         y = df['label']
#         # update the model
#         model.partial_fit(X, y, classes=[0, 1])
        
#         # evaluate the model and get the metrics
#         y_pred = model.predict(X)
#         accuracy = accuracy_score(y, y_pred)
#         precision = precision_score(y, y_pred, average='binary')
#         recall = recall_score(y, y_pred, average='binary')
#         f1 = f1_score(y, y_pred, average='binary')
        
#         return {'accuracy': accuracy, 'precision': precision, 'recall': recall, 'f1_score': f1}

# @app.route('/predict', methods=['POST'])
# def predict():
#     data = request.get_json()
#     df = pd.DataFrame(data)
    
#     # fit the model with the incoming data
#     X = df[['attrib1', 'attrib2', 'attrib3']]
#     y = df['label']
#     LightGBMModel.fit_model(X, y)
    
#     # make the prediction
#     y_pred = LightGBMModel.predict_model(X)
    
#     # calculate accuracy, precision, recall, and f1_score
#     accuracy = accuracy_score(y, y_pred)
#     precision = precision_score(y, y_pred)
#     recall = recall_score(y, y_pred)
#     f1 = f1_score(y, y_pred)
    
#     return jsonify({'result': y_pred, 'accuracy': accuracy, 'precision': precision, 'recall': recall, 'f1_score': f1})


    
# if __name__ == '__main__':
#     app.run(host="0.0.0.0", port=port)


    
    
    

