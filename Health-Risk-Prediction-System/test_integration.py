"""Integration test script for Health Risk Prediction System."""

import re

from app import app, ensure_project_ready
from utils.database import Admin, Feedback, Prediction, User, db


def csrf_from(client, url):
    """Extract CSRF token from form page."""
    html = client.get(url).data.decode()
    match = re.search(r'name="csrf_token" value="([^"]+)"', html)
    return match.group(1) if match else ""


def run_tests():
    """Execute end-to-end integration tests."""
    ensure_project_ready()
    client = app.test_client()

    for path in ["/", "/login", "/register", "/about", "/contact", "/admin/login"]:
        response = client.get(path)
        assert response.status_code == 200, f"Failed GET {path}"

    email = "integration@test.com"
    with app.app_context():
        existing = User.query.filter_by(email=email).first()
        if existing:
            Prediction.query.filter_by(user_id=existing.id).delete()
            Feedback.query.filter_by(user_id=existing.id).delete()
            User.query.filter_by(email=email).delete()
            db.session.commit()

    client.post(
        "/register",
        data={
            "csrf_token": csrf_from(client, "/register"),
            "name": "Integration User",
            "email": email,
            "password": "test123",
            "confirm_password": "test123",
        },
        follow_redirects=True,
    )

    client.post(
        "/login",
        data={
            "csrf_token": csrf_from(client, "/login"),
            "email": email,
            "password": "test123",
        },
        follow_redirects=True,
    )

    assert client.get("/dashboard").status_code == 200

    prediction_response = client.post(
        "/predict",
        data={
            "csrf_token": csrf_from(client, "/predict"),
            "age": "45",
            "gender": "Male",
            "height": "175",
            "weight": "85",
            "bmi": "27.76",
            "systolic_bp": "140",
            "diastolic_bp": "90",
            "heart_rate": "88",
            "blood_sugar": "130",
            "cholesterol": "240",
            "smoking": "Yes",
            "alcohol": "Occasionally",
            "exercise_frequency": "Rarely",
            "diet_quality": "Poor",
            "sleep_hours": "5",
            "stress_level": "High",
            "family_history": "Yes",
        },
        follow_redirects=True,
    )
    assert b"Risk" in prediction_response.data

    assert client.get("/history").status_code == 200
    assert client.get("/profile").status_code == 200

    client.post(
        "/feedback",
        data={
            "csrf_token": csrf_from(client, "/feedback"),
            "rating": "5",
            "feedback": "Excellent system, very helpful for health assessment.",
        },
        follow_redirects=True,
    )

    client.get("/logout")
    client.post(
        "/admin/login",
        data={
            "csrf_token": csrf_from(client, "/admin/login"),
            "username": "admin",
            "password": "Admin@123",
        },
        follow_redirects=True,
    )
    assert client.get("/admin/dashboard").status_code == 200

    with app.app_context():
        assert User.query.filter_by(email=email).first() is not None
        assert Prediction.query.count() >= 1
        assert Admin.query.count() >= 1
        assert Feedback.query.count() >= 1

    print("ALL INTEGRATION TESTS PASSED")


if __name__ == "__main__":
    run_tests()
