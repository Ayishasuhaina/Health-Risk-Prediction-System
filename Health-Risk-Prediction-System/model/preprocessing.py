"""Data preprocessing pipeline for health risk prediction."""

import os
import sys

import joblib
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder, StandardScaler

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, BASE_DIR)

from config import Config

CATEGORICAL_COLUMNS = [
    "Gender",
    "Smoking",
    "Alcohol",
    "PhysicalActivity",
    "ExerciseFrequency",
    "DietQuality",
    "StressLevel",
    "FamilyHistory",
    "Diabetes",
    "HeartDisease",
]

NUMERIC_COLUMNS = [
    "Age",
    "Height",
    "Weight",
    "BMI",
    "SystolicBP",
    "DiastolicBP",
    "HeartRate",
    "BloodSugar",
    "Cholesterol",
    "SleepHours",
]

TARGET_COLUMN = "RiskLevel"
FEATURE_COLUMNS = NUMERIC_COLUMNS + CATEGORICAL_COLUMNS


class DataPreprocessor:
    """Handles loading, cleaning, encoding, and scaling of health data."""

    def __init__(self):
        self.scaler = StandardScaler()
        self.label_encoders = {}
        self.target_encoder = LabelEncoder()
        self.feature_columns = FEATURE_COLUMNS.copy()

    def load_data(self, filepath=None):
        """Load dataset from CSV file."""
        path = filepath or Config.DATASET_PATH
        if not os.path.exists(path):
            raise FileNotFoundError(f"Dataset not found at {path}")
        return pd.read_csv(path)

    def clean_data(self, df):
        """Remove duplicates and handle missing values."""
        cleaned = df.copy()
        cleaned = cleaned.drop_duplicates()
        cleaned = cleaned.dropna()

        for column in NUMERIC_COLUMNS:
            cleaned[column] = pd.to_numeric(cleaned[column], errors="coerce")

        cleaned = cleaned.dropna()

        for column in CATEGORICAL_COLUMNS + [TARGET_COLUMN]:
            cleaned[column] = cleaned[column].astype(str).str.strip()

        return cleaned.reset_index(drop=True)

    def engineer_features(self, df):
        """Create additional engineered features."""
        engineered = df.copy()
        engineered["BP_Ratio"] = engineered["SystolicBP"] / (engineered["DiastolicBP"] + 1)
        engineered["RiskFactorCount"] = (
            (engineered["Smoking"] != "No").astype(int)
            + (engineered["Alcohol"] != "No").astype(int)
            + (engineered["FamilyHistory"] == "Yes").astype(int)
            + (engineered["Diabetes"] == "Yes").astype(int)
            + (engineered["HeartDisease"] == "Yes").astype(int)
        )
        engineered["ActivityScore"] = engineered["PhysicalActivity"].map(
            {"Sedentary": 1, "Light": 2, "Moderate": 3, "Active": 4, "Very Active": 5}
        ).fillna(2)
        engineered["ExerciseScore"] = engineered["ExerciseFrequency"].map(
            {"Never": 1, "Rarely": 2, "Sometimes": 3, "Often": 4, "Daily": 5}
        ).fillna(2)

        self.feature_columns = FEATURE_COLUMNS + [
            "BP_Ratio",
            "RiskFactorCount",
            "ActivityScore",
            "ExerciseScore",
        ]
        return engineered

    def encode_features(self, df, fit=True):
        """Encode categorical variables using label encoders."""
        encoded = df.copy()

        for column in CATEGORICAL_COLUMNS:
            if fit:
                encoder = LabelEncoder()
                encoded[column] = encoder.fit_transform(encoded[column].astype(str))
                self.label_encoders[column] = encoder
            else:
                encoder = self.label_encoders[column]
                values = encoded[column].astype(str)
                known_classes = set(encoder.classes_)
                values = values.apply(lambda item: item if item in known_classes else encoder.classes_[0])
                encoded[column] = encoder.transform(values)

        if fit:
            encoded[TARGET_COLUMN] = self.target_encoder.fit_transform(encoded[TARGET_COLUMN])
        else:
            encoded[TARGET_COLUMN] = self.target_encoder.transform(encoded[TARGET_COLUMN])

        return encoded

    def scale_features(self, x_train, x_test=None, fit=True):
        """Scale numeric and engineered features."""
        if fit:
            x_train_scaled = self.scaler.fit_transform(x_train)
            if x_test is not None:
                x_test_scaled = self.scaler.transform(x_test)
                return x_train_scaled, x_test_scaled
            return x_train_scaled
        return self.scaler.transform(x_train)

    def prepare_training_data(self, df):
        """Full preprocessing pipeline for model training."""
        cleaned = self.clean_data(df)
        engineered = self.engineer_features(cleaned)
        encoded = self.encode_features(engineered, fit=True)

        x_data = encoded[self.feature_columns]
        y_data = encoded[TARGET_COLUMN]

        x_train, x_test, y_train, y_test = train_test_split(
            x_data, y_data, test_size=0.2, random_state=42, stratify=y_data
        )

        x_train_scaled, x_test_scaled = self.scale_features(x_train, x_test, fit=True)
        return x_train_scaled, x_test_scaled, y_train, y_test, engineered

    def save_artifacts(self):
        """Persist scaler and encoders."""
        os.makedirs(os.path.dirname(Config.SCALER_PATH), exist_ok=True)
        joblib.dump(self.scaler, Config.SCALER_PATH)
        joblib.dump(
            {
                "label_encoders": self.label_encoders,
                "target_encoder": self.target_encoder,
                "feature_columns": self.feature_columns,
            },
            Config.ENCODERS_PATH,
        )

    def load_artifacts(self):
        """Load persisted scaler and encoders."""
        self.scaler = joblib.load(Config.SCALER_PATH)
        artifacts = joblib.load(Config.ENCODERS_PATH)
        self.label_encoders = artifacts["label_encoders"]
        self.target_encoder = artifacts["target_encoder"]
        self.feature_columns = artifacts["feature_columns"]

    def transform_input(self, input_dict):
        """Transform single prediction input to model-ready array."""
        if not self.label_encoders:
            self.load_artifacts()

        row = pd.DataFrame([input_dict])
        row = self.engineer_features(row)

        for column in CATEGORICAL_COLUMNS:
            encoder = self.label_encoders[column]
            value = str(input_dict.get(column, encoder.classes_[0]))
            if value not in encoder.classes_:
                value = encoder.classes_[0]
            row[column] = encoder.transform([value])[0]

        features = row[self.feature_columns]
        scaled = self.scaler.transform(features)
        return scaled
