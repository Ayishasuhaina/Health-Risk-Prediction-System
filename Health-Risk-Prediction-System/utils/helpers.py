"""Helper utilities for the application."""

import os
from datetime import datetime
from functools import wraps

from flask import flash, redirect, session, url_for


def login_required(view_func):
    """Decorator to require authenticated user session."""

    @wraps(view_func)
    def wrapper(*args, **kwargs):
        if "user_id" not in session:
            flash("Please log in to access this page.", "warning")
            return redirect(url_for("login"))
        return view_func(*args, **kwargs)

    return wrapper


def admin_required(view_func):
    """Decorator to require authenticated admin session."""

    @wraps(view_func)
    def wrapper(*args, **kwargs):
        if "admin_id" not in session:
            flash("Admin access required.", "warning")
            return redirect(url_for("admin_login"))
        return view_func(*args, **kwargs)

    return wrapper


def calculate_bmi(weight, height_cm):
    """Calculate BMI from weight (kg) and height (cm)."""
    height_m = height_cm / 100.0
    if height_m <= 0:
        return 0.0
    return round(weight / (height_m ** 2), 2)


def ensure_directory(path):
    """Create directory if it does not exist."""
    os.makedirs(path, exist_ok=True)


def format_datetime(value):
    """Format datetime for display."""
    if not value:
        return ""
    if isinstance(value, str):
        return value
    return value.strftime("%Y-%m-%d %H:%M")


def get_monthly_statistics(predictions):
    """Aggregate prediction counts by month."""
    stats = {}
    for prediction in predictions:
        month_key = prediction.created_at.strftime("%Y-%m")
        if month_key not in stats:
            stats[month_key] = {"Low Risk": 0, "Medium Risk": 0, "High Risk": 0, "total": 0}
        stats[month_key][prediction.prediction] = stats[month_key].get(prediction.prediction, 0) + 1
        stats[month_key]["total"] += 1
    return stats


def risk_badge_class(risk_level):
    """Return Bootstrap badge class for risk level."""
    mapping = {
        "Low Risk": "success",
        "Medium Risk": "warning",
        "High Risk": "danger",
    }
    return mapping.get(risk_level, "secondary")


def generate_report_filename(user_name):
    """Generate unique PDF report filename."""
    timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    safe_name = "".join(char for char in user_name if char.isalnum() or char in ("_", "-")).lower()
    return f"health_report_{safe_name}_{timestamp}.pdf"
