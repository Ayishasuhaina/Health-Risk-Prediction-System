"""Input validation utilities."""

import re


EMAIL_PATTERN = re.compile(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$")


def validate_email(email):
    """Validate email format."""
    if not email or not EMAIL_PATTERN.match(email.strip()):
        return False, "Please enter a valid email address."
    return True, ""


def validate_password(password):
    """Validate password strength."""
    if not password or len(password) < 6:
        return False, "Password must be at least 6 characters long."
    return True, ""


def validate_name(name):
    """Validate user name."""
    if not name or len(name.strip()) < 2:
        return False, "Name must be at least 2 characters long."
    return True, ""


def validate_registration(name, email, password, confirm_password):
    """Validate registration form data."""
    valid, message = validate_name(name)
    if not valid:
        return False, message

    valid, message = validate_email(email)
    if not valid:
        return False, message

    valid, message = validate_password(password)
    if not valid:
        return False, message

    if password != confirm_password:
        return False, "Passwords do not match."

    return True, ""


def validate_numeric(value, field_name, min_val, max_val):
    """Validate numeric field within range."""
    try:
        number = float(value)
    except (TypeError, ValueError):
        return False, f"{field_name} must be a valid number."

    if number < min_val or number > max_val:
        return False, f"{field_name} must be between {min_val} and {max_val}."

    return True, ""


def validate_prediction_form(form_data):
    """Validate prediction form inputs."""
    errors = []

    checks = [
        ("age", "Age", 1, 120),
        ("height", "Height", 100, 250),
        ("weight", "Weight", 30, 300),
        ("bmi", "BMI", 10, 60),
        ("systolic_bp", "Systolic BP", 70, 220),
        ("diastolic_bp", "Diastolic BP", 40, 140),
        ("heart_rate", "Heart Rate", 40, 200),
        ("blood_sugar", "Blood Sugar", 50, 400),
        ("cholesterol", "Cholesterol", 100, 400),
        ("sleep_hours", "Sleep Hours", 1, 16),
    ]

    for field, label, min_val, max_val in checks:
        valid, message = validate_numeric(form_data.get(field), label, min_val, max_val)
        if not valid:
            errors.append(message)

    categorical_fields = {
        "gender": ["Male", "Female", "Other"],
        "smoking": ["No", "Occasionally", "Yes"],
        "alcohol": ["No", "Occasionally", "Yes"],
        "exercise_frequency": ["Never", "Rarely", "Sometimes", "Often", "Daily"],
        "diet_quality": ["Poor", "Average", "Good", "Excellent"],
        "stress_level": ["Low", "Moderate", "High", "Very High"],
        "family_history": ["No", "Yes"],
    }

    for field, allowed in categorical_fields.items():
        value = form_data.get(field, "").strip()
        if value not in allowed:
            errors.append(f"Invalid value selected for {field.replace('_', ' ').title()}.")

    return len(errors) == 0, errors


def validate_feedback(feedback_text, rating):
    """Validate feedback submission."""
    if not feedback_text or len(feedback_text.strip()) < 10:
        return False, "Feedback must be at least 10 characters long."

    try:
        rating_value = int(rating)
    except (TypeError, ValueError):
        return False, "Rating must be a number between 1 and 5."

    if rating_value < 1 or rating_value > 5:
        return False, "Rating must be between 1 and 5."

    return True, ""
