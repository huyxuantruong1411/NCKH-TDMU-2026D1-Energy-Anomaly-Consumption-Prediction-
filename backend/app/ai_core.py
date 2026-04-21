import os
import json
import xgboost as xgb
import numpy as np
from collections import deque, defaultdict

class AnomalyDetector:
    def __init__(self):
        self.model = xgb.Booster()
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        model_path = os.path.join(base_dir, "models_ai", "xgboost_forecasting_optuna.json")
        self.model.load_model(model_path)
        
        self.residuals_history = defaultdict(lambda: deque(maxlen=168))
        self.features_history = defaultdict(lambda: deque(maxlen=168))
        self.k_factor = 3.0 
        self.feature_names = self.model.feature_names if self.model.feature_names else []

    def predict_and_detect(self, building_name, actual_load, features_array):
        input_data = np.array([features_array]) 
        dmatrix = xgb.DMatrix(input_data, feature_names=self.model.feature_names)
        pred_log = self.model.predict(dmatrix)[0]
        predicted_load = float(np.expm1(pred_log))
        
        error = abs(actual_load - predicted_load)
        
        history = self.residuals_history[building_name]
        history.append(error)
        feat_hist = self.features_history[building_name]
        feat_hist.append(features_array)
        
        if len(history) < 24: 
            anomaly_threshold = actual_load * 0.1 
        else:
            q75, q25 = np.percentile(history, [75, 25])
            iqr = q75 - q25
            median_res = np.median(history)
            dynamic_threshold = median_res + (self.k_factor * iqr)
            anomaly_threshold = max(dynamic_threshold, actual_load * 0.1)
        
        is_anomaly = 1 if error > anomaly_threshold else 0
        
        explanation_json = "{}"
        if is_anomaly == 1 and len(feat_hist) > 5 and self.feature_names:
            baseline = np.mean(list(feat_hist)[:-1], axis=0)
            current = np.array(features_array)
            diff = np.abs(current - baseline) / (np.abs(baseline) + 1e-5)
            ignore_feats = {'building_id', 'hour', 'dayofweek', 'month', 'is_weekend', 'hour_sin', 'hour_cos'}
            explanation_data = {}
            top_indices = np.argsort(diff)[::-1]
            count = 0
            for idx in top_indices:
                feat_name = self.feature_names[idx]
                if feat_name in ignore_feats: continue 
                percent_change = ((current[idx] - baseline[idx]) / (abs(baseline[idx]) + 1e-5)) * 100
                explanation_data[feat_name] = round(percent_change, 2)
                count += 1
                if count >= 5: break # [FIX] Trích xuất 5 độ đo lớn nhất
            explanation_json = json.dumps(explanation_data)

        temp, dew, wind, pressure = 0.0, 0.0, 0.0, 0.0
        if 'airTemperature' in self.feature_names: temp = float(features_array[self.feature_names.index('airTemperature')])
        if 'dewTemperature' in self.feature_names: dew = float(features_array[self.feature_names.index('dewTemperature')])
        if 'windSpeed' in self.feature_names: wind = float(features_array[self.feature_names.index('windSpeed')])
        if 'seaLvlPressure' in self.feature_names: pressure = float(features_array[self.feature_names.index('seaLvlPressure')])

        return predicted_load, is_anomaly, float(anomaly_threshold), temp, dew, wind, pressure, explanation_json

detector = AnomalyDetector()