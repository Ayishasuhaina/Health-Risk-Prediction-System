"""Launcher for Health Risk Prediction System from workspace root."""

import os
import runpy
import sys

PROJECT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "Health-Risk-Prediction-System")

if not os.path.isdir(PROJECT_DIR):
    raise SystemExit("Health-Risk-Prediction-System folder not found.")

os.chdir(PROJECT_DIR)
sys.path.insert(0, PROJECT_DIR)
runpy.run_path(os.path.join(PROJECT_DIR, "app.py"), run_name="__main__")
