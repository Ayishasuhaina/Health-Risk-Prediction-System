"""Generate synthetic health risk dataset."""

import os
import sys

import numpy as np
import pandas as pd

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, BASE_DIR)

DATASET_DIR = os.path.join(BASE_DIR, "dataset")
OUTPUT_PATH = os.path.join(DATASET_DIR, "health_risk_dataset.csv")

GENDERS = ["Male", "Female", "Other"]
SMOKING = ["No", "Occasionally", "Yes"]
ALCOHOL = ["No", "Occasionally", "Yes"]
PHYSICAL_ACTIVITY = ["Sedentary", "Light", "Moderate", "Active", "Very Active"]
EXERCISE_FREQUENCY = ["Never", "Rarely", "Sometimes", "Often", "Daily"]
DIET_QUALITY = ["Poor", "Average", "Good", "Excellent"]
STRESS_LEVEL = ["Low", "Moderate", "High", "Very High"]
YES_NO = ["No", "Yes"]
RISK_LEVELS = ["Low Risk", "Medium Risk", "High Risk"]


def generate_row(rng):
    """Generate a single realistic health record."""
    age = int(rng.integers(18, 85))
    gender = rng.choice(GENDERS, p=[0.48, 0.48, 0.04])
    height = round(rng.uniform(150, 195), 1)
    weight = round(rng.uniform(45, 130), 1)
    bmi = round(weight / ((height / 100) ** 2), 2)

    smoking = rng.choice(SMOKING, p=[0.55, 0.25, 0.20])
    alcohol = rng.choice(ALCOHOL, p=[0.50, 0.30, 0.20])
    physical_activity = rng.choice(PHYSICAL_ACTIVITY, p=[0.20, 0.25, 0.25, 0.20, 0.10])
    exercise_frequency = rng.choice(EXERCISE_FREQUENCY, p=[0.15, 0.20, 0.25, 0.25, 0.15])
    diet_quality = rng.choice(DIET_QUALITY, p=[0.15, 0.35, 0.35, 0.15])
    sleep_hours = round(rng.uniform(4.5, 10.5), 1)
    stress_level = rng.choice(STRESS_LEVEL, p=[0.25, 0.35, 0.25, 0.15])
    family_history = rng.choice(YES_NO, p=[0.65, 0.35])

    systolic_bp = int(np.clip(rng.normal(120, 18), 90, 200))
    diastolic_bp = int(np.clip(rng.normal(78, 12), 55, 130))
    heart_rate = int(np.clip(rng.normal(74, 12), 50, 130))
    blood_sugar = round(np.clip(rng.normal(105, 25), 70, 350), 1)
    cholesterol = int(np.clip(rng.normal(190, 35), 120, 350))

    diabetes = "Yes" if blood_sugar > 140 and rng.random() > 0.3 else "No"
    if family_history == "Yes" and rng.random() > 0.6:
        diabetes = "Yes"

    heart_disease = "No"
    if age > 55 and (systolic_bp > 140 or cholesterol > 240) and rng.random() > 0.5:
        heart_disease = "Yes"
    if family_history == "Yes" and age > 45 and rng.random() > 0.55:
        heart_disease = "Yes"

    risk_score = 0.0
    risk_score += max(0, (age - 40) * 0.08)
    risk_score += max(0, (bmi - 25) * 0.15)
    risk_score += max(0, (systolic_bp - 120) * 0.04)
    risk_score += max(0, (diastolic_bp - 80) * 0.05)
    risk_score += max(0, (blood_sugar - 100) * 0.03)
    risk_score += max(0, (cholesterol - 200) * 0.02)
    risk_score += max(0, (heart_rate - 80) * 0.03)

    risk_map = {"No": 0, "Occasionally": 1, "Yes": 2}
    risk_score += risk_map[smoking] * 1.2
    risk_score += risk_map[alcohol] * 0.8

    activity_map = {"Sedentary": 2.5, "Light": 1.5, "Moderate": 0.8, "Active": 0.3, "Very Active": 0.0}
    risk_score += activity_map[physical_activity]

    exercise_map = {"Never": 2.0, "Rarely": 1.5, "Sometimes": 1.0, "Often": 0.4, "Daily": 0.0}
    risk_score += exercise_map[exercise_frequency]

    diet_map = {"Poor": 2.0, "Average": 1.0, "Good": 0.4, "Excellent": 0.0}
    risk_score += diet_map[diet_quality]

    stress_map = {"Low": 0.0, "Moderate": 0.8, "High": 1.5, "Very High": 2.2}
    risk_score += stress_map[stress_level]

    if sleep_hours < 6:
        risk_score += 1.2
    elif sleep_hours > 9:
        risk_score += 0.5

    if family_history == "Yes":
        risk_score += 1.5
    if diabetes == "Yes":
        risk_score += 2.5
    if heart_disease == "Yes":
        risk_score += 3.0

    noise = rng.normal(0, 1.2)
    final_score = risk_score + noise

    if final_score < 8:
        risk_level = "Low Risk"
    elif final_score < 16:
        risk_level = "Medium Risk"
    else:
        risk_level = "High Risk"

    return {
        "Age": age,
        "Gender": gender,
        "Height": height,
        "Weight": weight,
        "BMI": bmi,
        "SystolicBP": systolic_bp,
        "DiastolicBP": diastolic_bp,
        "HeartRate": heart_rate,
        "BloodSugar": blood_sugar,
        "Cholesterol": cholesterol,
        "Smoking": smoking,
        "Alcohol": alcohol,
        "PhysicalActivity": physical_activity,
        "ExerciseFrequency": exercise_frequency,
        "DietQuality": diet_quality,
        "SleepHours": sleep_hours,
        "StressLevel": stress_level,
        "FamilyHistory": family_history,
        "Diabetes": diabetes,
        "HeartDisease": heart_disease,
        "RiskLevel": risk_level,
    }


def balance_classes(df, rng, target_per_class=5000):
    """Balance dataset to equal class distribution."""
    balanced_frames = []
    for risk in RISK_LEVELS:
        subset = df[df["RiskLevel"] == risk]
        if len(subset) >= target_per_class:
            balanced_frames.append(subset.sample(n=target_per_class, random_state=42))
        else:
            needed = target_per_class - len(subset)
            extra_rows = []
            while len(extra_rows) < needed:
                row = generate_row(rng)
                if row["RiskLevel"] == risk:
                    extra_rows.append(row)
            extra_df = pd.DataFrame(extra_rows)
            balanced_frames.append(pd.concat([subset, extra_df], ignore_index=True))

    balanced = pd.concat(balanced_frames, ignore_index=True)
    return balanced.sample(frac=1, random_state=42).reset_index(drop=True)


def main():
    """Generate and save balanced synthetic dataset."""
    os.makedirs(DATASET_DIR, exist_ok=True)
    rng = np.random.default_rng(42)

    rows = [generate_row(rng) for _ in range(18000)]
    df = pd.DataFrame(rows)
    df = df.drop_duplicates().reset_index(drop=True)
    df = balance_classes(df, rng, target_per_class=5000)

    df = df.drop_duplicates().reset_index(drop=True)
    assert df.isnull().sum().sum() == 0
    assert len(df) >= 15000

    df.to_csv(OUTPUT_PATH, index=False)
    print(f"Dataset saved to {OUTPUT_PATH} with {len(df)} rows.")
    print(df["RiskLevel"].value_counts())


if __name__ == "__main__":
    main()
