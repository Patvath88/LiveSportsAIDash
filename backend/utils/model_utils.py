import xgboost as xgb
import joblib
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
import pandas as pd
import numpy as np
import os

MODEL_PATH = "data/xgb_model.pkl"

def train_xgb_model(df):
    X = df.drop(columns=["target"])
    y = df["target"]
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    model = xgb.XGBClassifier(n_estimators=100, learning_rate=0.1, max_depth=5)
    model.fit(X_train, y_train)
    preds = model.predict(X_test)
    acc = accuracy_score(y_test, preds)

    os.makedirs("data", exist_ok=True)
    joblib.dump(model, MODEL_PATH)
    return acc

def predict_with_model(df):
    model = joblib.load(MODEL_PATH)
    preds = model.predict(df)
    return preds
