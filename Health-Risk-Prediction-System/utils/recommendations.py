"""Health recommendations based on risk level and user profile."""


def get_lifestyle_suggestions(risk_level, form_data):
    """Return lifestyle suggestions tailored to risk and habits."""
    suggestions = []

    if form_data.get("smoking") in ("Yes", "Occasionally"):
        suggestions.append("Reduce or quit smoking to lower cardiovascular and respiratory risk.")

    if form_data.get("alcohol") in ("Yes", "Occasionally"):
        suggestions.append("Limit alcohol intake to moderate levels as recommended by health guidelines.")

    sleep_hours = float(form_data.get("sleep_hours", 7))
    if sleep_hours < 6:
        suggestions.append("Aim for 7-8 hours of quality sleep each night to support recovery and immunity.")
    elif sleep_hours > 10:
        suggestions.append("Maintain a consistent sleep schedule and avoid excessive sleep duration.")

    if form_data.get("stress_level") in ("High", "Very High"):
        suggestions.append("Practice stress management techniques such as meditation, deep breathing, or yoga.")

    if risk_level == "High Risk":
        suggestions.append("Schedule regular health check-ups and monitor vital signs weekly.")
    elif risk_level == "Medium Risk":
        suggestions.append("Adopt preventive health habits and track progress monthly.")
    else:
        suggestions.append("Maintain your current healthy lifestyle and continue annual wellness visits.")

    if not suggestions:
        suggestions.append("Continue balanced daily routines and stay physically active.")

    return suggestions


def get_diet_recommendations(risk_level, form_data):
    """Return diet recommendations."""
    recommendations = [
        "Increase intake of fruits, vegetables, whole grains, and lean proteins.",
        "Reduce processed foods, refined sugar, and excessive salt consumption.",
        "Stay hydrated by drinking at least 8 glasses of water daily.",
    ]

    diet_quality = form_data.get("diet_quality", "Average")
    if diet_quality in ("Poor", "Average"):
        recommendations.append("Plan structured meals with portion control and balanced macronutrients.")

    cholesterol = float(form_data.get("cholesterol", 200))
    if cholesterol > 240:
        recommendations.append("Choose heart-healthy fats and limit saturated and trans fats.")

    blood_sugar = float(form_data.get("blood_sugar", 100))
    if blood_sugar > 140:
        recommendations.append("Monitor carbohydrate intake and prefer low glycemic index foods.")

    if risk_level == "High Risk":
        recommendations.append("Consult a nutritionist for a personalized meal plan.")

    return recommendations


def get_exercise_recommendations(risk_level, form_data):
    """Return exercise recommendations."""
    exercise_freq = form_data.get("exercise_frequency", "Sometimes")
    recommendations = []

    if exercise_freq in ("Never", "Rarely"):
        recommendations.extend([
            "Start with 20-30 minutes of brisk walking at least 5 days per week.",
            "Include light strength training twice weekly to improve metabolism.",
        ])
    elif exercise_freq == "Sometimes":
        recommendations.extend([
            "Increase aerobic activity to 150 minutes per week at moderate intensity.",
            "Add flexibility and balance exercises to your routine.",
        ])
    else:
        recommendations.extend([
            "Maintain regular cardio and strength training for overall fitness.",
            "Include recovery days to prevent overtraining and injury.",
        ])

    if risk_level == "High Risk":
        recommendations.append("Seek medical clearance before starting intensive exercise programs.")

    return recommendations


def get_medical_advice(risk_level, form_data):
    """Return medical advice based on risk assessment."""
    advice = []

    systolic = float(form_data.get("systolic_bp", 120))
    diastolic = float(form_data.get("diastolic_bp", 80))
    if systolic >= 140 or diastolic >= 90:
        advice.append("Your blood pressure readings suggest hypertension risk. Consult a physician promptly.")

    heart_rate = float(form_data.get("heart_rate", 72))
    if heart_rate > 100:
        advice.append("Elevated resting heart rate detected. Consider a cardiovascular evaluation.")

    if form_data.get("family_history") == "Yes":
        advice.append("Family history indicates genetic predisposition. Regular screening is recommended.")

    if risk_level == "High Risk":
        advice.extend([
            "Immediate medical consultation is strongly advised.",
            "Complete blood work, lipid profile, and cardiac assessment as recommended by your doctor.",
        ])
    elif risk_level == "Medium Risk":
        advice.extend([
            "Schedule a preventive health check-up within the next 3 months.",
            "Monitor blood pressure, blood sugar, and cholesterol regularly.",
        ])
    else:
        advice.append("Continue preventive care with annual health screenings.")

    return advice


def build_full_recommendation(risk_level, form_data):
    """Combine all recommendation categories into structured text."""
    sections = {
        "Lifestyle Suggestions": get_lifestyle_suggestions(risk_level, form_data),
        "Diet Recommendations": get_diet_recommendations(risk_level, form_data),
        "Exercise Recommendations": get_exercise_recommendations(risk_level, form_data),
        "Medical Advice": get_medical_advice(risk_level, form_data),
    }

    lines = []
    for title, items in sections.items():
        lines.append(f"{title}:")
        for item in items:
            lines.append(f"- {item}")
        lines.append("")

    return "\n".join(lines).strip(), sections
