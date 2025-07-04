from flask import Flask, jsonify, request
from river import linear_model
from river import metrics
from river import evaluate
from river import preprocessing
from river import compose
from beta_distribution_drift_detector.bdddc import BDDDC
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
#import lightgbm as lgb
from river import metrics
from river import stream
import joblib
import json
import os

app = Flask(__name__)
port = 5000

class RiverML:
    # Fraud detection model
    model = compose.Pipeline(
        preprocessing.StandardScaler(),
        linear_model.LogisticRegression()
    )
    
    # ROCAUC metric to score the model as it trains
    metric = metrics.ROCAUC()

    # Beta distribution drift detector to detect drift
    change_detector = BDDDC()

    # Counter to keep track of the number of samples seen so far
    sample_count = 0

fraud_model = RiverML()

@app.route('/predict', methods=['POST'])
def predict():
    # Convert into dict
    request_data = request.get_json()
    x_data = json.loads(request_data['x'])
    y_data = json.loads(request_data['y'])

    # Do the prediction and score it
    y_pred = fraud_model.model.predict_one(x_data)

    # Add the element to the change detector
    try:
        fraud_model.change_detector.add_element(np.array(y_true=y_data, y_pred=y_pred))
    except:
        pass

    # Check for drift
    if fraud_model.sample_count > 0 and fraud_model.change_detector.change_detected:
        print("Drift detected!")

        # Retrain the model
        fraud_model.model = compose.Pipeline(
            preprocessing.StandardScaler(),
            linear_model.LogisticRegression()
        )
        fraud_model.metric = metrics.ROCAUC()
        fraud_model.change_detector = BDDDC()
        evaluate.progressive_val_score(x_data, y_data, fraud_model.model, fraud_model.metric)
        fraud_model.sample_count = 0
    else:
        # Update the model and the metric
        y_pred = fraud_model.model.predict_one(x_data)
        fraud_model.metric.update(y_data, y_pred)
        fraud_model.model.learn_one(x_data, y_data)
        fraud_model.sample_count += 1

    return jsonify({'result': y_pred, 'performance': {'ROCAUC': fraud_model.metric.get()}})

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=port)
