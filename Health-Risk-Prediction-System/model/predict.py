"""Prediction module for health risk assessment."""

import os
import sys

import joblib
import numpy as np

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, BASE_DIR)

from config import Config
from model.preprocessing import DataPreprocessor


class HealthRiskPredictor:
    """Load trained model and perform health risk predictions."""

    def __init__(self):
        self.model = None
        self.preprocessor = DataPreprocessor()
        self._loaded = False

    def load_model(self):
        """Load model and preprocessing artifacts."""
        if not os.path.exists(Config.MODEL_PATH):
            raise FileNotFoundError(
                "Trained model not found. Run model/train_model.py first."
            )
        self.model = joblib.load(Config.MODEL_PATH)
        self.preprocessor.load_artifacts()
        self._loaded = True

    def _map_form_to_features(self, form_data):
        """Map web form data to model feature dictionary."""
        exercise_freq = form_data.get("exercise_frequency", "Sometimes")
        activity_map = {
            "Never": "Sedentary",
            "Rarely": "Light",
            "Sometimes": "Moderate",
            "Often": "Active",
            "Daily": "Very Active",
        }

        blood_sugar = float(form_data.get("blood_sugar", 100))
        family_history = form_data.get("family_history", "No")
        age = float(form_data.get("age", 30))
        systolic = float(form_data.get("systolic_bp", 120))
        cholesterol = float(form_data.get("cholesterol", 200))

        diabetes = "Yes" if blood_sugar > 140 else "No"
        heart_disease = "No"
        if age > 55 and (systolic > 140 or cholesterol > 240):
            heart_disease = "Yes"
        if family_history == "Yes" and age > 45 and systolic > 130:
            heart_disease = "Yes"

        return {
            "Age": float(form_data.get("age")),
            "Gender": form_data.get("gender"),
            "Height": float(form_data.get("height")),
            "Weight": float(form_data.get("weight")),
            "BMI": float(form_data.get("bmi")),
            "SystolicBP": float(form_data.get("systolic_bp")),
            "DiastolicBP": float(form_data.get("diastolic_bp")),
            "HeartRate": float(form_data.get("heart_rate")),
            "BloodSugar": blood_sugar,
            "Cholesterol": cholesterol,
            "Smoking": form_data.get("smoking"),
            "Alcohol": form_data.get("alcohol"),
            "PhysicalActivity": activity_map.get(exercise_freq, "Moderate"),
            "ExerciseFrequency": exercise_freq,
            "DietQuality": form_data.get("diet_quality"),
            "SleepHours": float(form_data.get("sleep_hours")),
            "StressLevel": form_data.get("stress_level"),
            "FamilyHistory": family_history,
            "Diabetes": diabetes,
            "HeartDisease": heart_disease,
        }

    def predict(self, form_data):
        """Predict health risk from form input."""
        if not self._loaded:
            self.load_model()

        features = self._map_form_to_features(form_data)
        scaled_input = self.preprocessor.transform_input(features)

        probabilities = self.model.predict_proba(scaled_input)[0]
        predicted_class = self.model.predict(scaled_input)[0]
        risk_level = self.preprocessor.target_encoder.inverse_transform([predicted_class])[0]

        confidence = float(np.max(probabilities) * 100)
        class_labels = list(self.preprocessor.target_encoder.classes_)
        prob_dict = {
            label: round(float(prob) * 100, 2)
            for label, prob in zip(class_labels, probabilities)
        }

        risk_percentage = prob_dict.get(risk_level, confidence)

        return {
            "prediction": risk_level,
            "confidence": round(confidence, 2),
            "probability": prob_dict,
            "risk_percentage": risk_percentage,
            "features": features,
        }


predictor = HealthRiskPredictor()
