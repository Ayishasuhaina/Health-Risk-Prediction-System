"""Application configuration settings."""

import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))


class Config:
    """Base configuration for the Health Risk Prediction System."""

    SECRET_KEY = os.environ.get("SECRET_KEY", "health-risk-prediction-secret-key-2026")
    SQLALCHEMY_DATABASE_URI = "sqlite:///" + os.path.join(BASE_DIR, "database", "database.db")
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    DATASET_PATH = os.path.join(BASE_DIR, "dataset", "health_risk_dataset.csv")
    MODEL_PATH = os.path.join(BASE_DIR, "trained_model", "model.pkl")
    SCALER_PATH = os.path.join(BASE_DIR, "trained_model", "scaler.pkl")
    ENCODERS_PATH = os.path.join(BASE_DIR, "trained_model", "label_encoders.pkl")
    REPORTS_DIR = os.path.join(BASE_DIR, "static", "reports")
    IMAGES_DIR = os.path.join(BASE_DIR, "static", "images")

    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"
    PERMANENT_SESSION_LIFETIME = 3600

    DEFAULT_ADMIN_USERNAME = "admin"
    DEFAULT_ADMIN_PASSWORD = "Admin@123"
