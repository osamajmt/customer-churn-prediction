import joblib
import numpy as np
import pandas as pd
import os
from django.shortcuts import render

from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
import json

# Load model 
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

model = joblib.load(os.path.join(BASE_DIR, "model.pkl"))
scaler = joblib.load(os.path.join(BASE_DIR, "scaler.pkl"))
columns = joblib.load(os.path.join(BASE_DIR, "columns.pkl"))


def predict_churn(request):
    if request.method == "GET":
        return render(request, "predictor/index.html")

    if request.method == "POST":
        try:
            data = request.POST

            
            input_df = pd.DataFrame([{}])
            input_df = input_df.reindex(columns=columns, fill_value=0)

            # Numeric features
            numeric_fields = ["tenure", "MonthlyCharges", "TotalCharges"]
            for field in numeric_fields:
                value = data.get(field)
                if value:
                    input_df[field] = float(value)

            # categorical encoding 
            for col in columns:
                if "_" in col:
                    base, value = col.split("_", 1)
                    if data.get(base) == value:
                        input_df[col] = 1

            # Scale + predict
            features_scaled = scaler.transform(input_df)

            prediction = model.predict(features_scaled)[0]
            proba = model.predict_proba(features_scaled)[0][1]

            result = "Will Churn ❌" if prediction == 1 else "Will Stay ✅"

            return render(request, "predictor/index.html", {
                "result": result,
                "prob": round(proba * 100, 2)
            })

        except Exception as e:
            return render(request, "predictor/index.html", {
                "result": f"Error: {str(e)}"
            })



@csrf_exempt
def predict_api(request):
    if request.method == "POST":
        try:
            # Parse JSON body
           data = json.loads(request.body)

           input_df = pd.DataFrame([{}])
           input_df = input_df.reindex(columns=columns, fill_value=0)

            # Numeric features
           numeric_fields = ["tenure", "MonthlyCharges", "TotalCharges"]
           for field in numeric_fields:
                value = data.get(field)
                if value is not None:
                    input_df[field] = float(value)
            # categorical encoding
           for col in columns:
                if "_" in col:
                    base, value = col.split("_", 1)
                    if data.get(base) == value:
                        input_df[col] = 1

            # Prediction
           features_scaled = scaler.transform(input_df)

           prediction = int(model.predict(features_scaled)[0])
           proba = float(model.predict_proba(features_scaled)[0][1])

           result = "Will Churn ❌" if prediction == 1 else "Will Stay ✅"

           return JsonResponse({
                "prediction": prediction,
                "result": result,
                "probability": round(proba, 4)
            })

        except Exception as e:
            return JsonResponse({"error": str(e)})

    return JsonResponse({"message": "Send POST request"})