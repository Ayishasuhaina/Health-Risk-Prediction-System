"""Health Risk Prediction System - Main Flask Application."""

import os
import sys
from datetime import datetime

from flask import (
    Flask,
    flash,
    jsonify,
    redirect,
    render_template,
    request,
    send_from_directory,
    session,
    url_for,
)
from flask_wtf.csrf import CSRFProtect
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
sys.path.insert(0, BASE_DIR)

from config import Config
from model.predict import predictor
from utils.database import Admin, Feedback, Prediction, User, db, init_db
from utils.helpers import (
    admin_required,
    calculate_bmi,
    ensure_directory,
    format_datetime,
    generate_report_filename,
    get_monthly_statistics,
    login_required,
    risk_badge_class,
)
from utils.recommendations import build_full_recommendation
from utils.validators import (
    validate_email,
    validate_feedback,
    validate_name,
    validate_password,
    validate_prediction_form,
    validate_registration,
)

app = Flask(__name__)
app.config.from_object(Config)
csrf = CSRFProtect(app)
db.init_app(app)


def ensure_project_ready():
    """Ensure dataset, model, and directories exist before serving."""
    ensure_directory(os.path.join(BASE_DIR, "database"))
    ensure_directory(Config.REPORTS_DIR)
    ensure_directory(Config.IMAGES_DIR)
    ensure_directory(os.path.join(BASE_DIR, "trained_model"))

    if not os.path.exists(Config.DATASET_PATH):
        from dataset.generate_dataset import main as generate_dataset
        generate_dataset()

    if not os.path.exists(Config.MODEL_PATH):
        from model.train_model import train_and_select_best_model
        train_and_select_best_model()

    init_db(app, Config.DEFAULT_ADMIN_USERNAME, Config.DEFAULT_ADMIN_PASSWORD)
    predictor.load_model()


@app.context_processor
def inject_globals():
    """Inject common template variables."""
    return {
        "current_year": datetime.utcnow().year,
        "user_name": session.get("user_name"),
        "is_admin": "admin_id" in session,
        "is_logged_in": "user_id" in session,
        "risk_badge_class": risk_badge_class,
        "format_datetime": format_datetime,
    }


@app.route("/")
def index():
    """Landing page."""
    return render_template("index.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    """User registration."""
    if "user_id" in session:
        return redirect(url_for("dashboard"))

    if request.method == "POST":
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        confirm_password = request.form.get("confirm_password", "")

        valid, message = validate_registration(name, email, password, confirm_password)
        if not valid:
            flash(message, "danger")
            return render_template("register.html")

        if User.query.filter_by(email=email).first():
            flash("Email already registered. Please login.", "warning")
            return redirect(url_for("login"))

        user = User(name=name, email=email)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()

        flash("Registration successful. Please log in.", "success")
        return redirect(url_for("login"))

    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    """User login."""
    if "user_id" in session:
        return redirect(url_for("dashboard"))

    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")

        valid, message = validate_email(email)
        if not valid:
            flash(message, "danger")
            return render_template("login.html")

        user = User.query.filter_by(email=email).first()
        if user and user.check_password(password):
            session.clear()
            session.permanent = True
            session["user_id"] = user.id
            session["user_name"] = user.name
            session["user_email"] = user.email
            flash(f"Welcome back, {user.name}!", "success")
            return redirect(url_for("dashboard"))

        flash("Invalid email or password.", "danger")

    return render_template("login.html")


@app.route("/logout")
def logout():
    """User logout."""
    session.clear()
    flash("You have been logged out.", "info")
    return redirect(url_for("index"))


@app.route("/forgot-password", methods=["GET", "POST"])
def forgot_password():
    """Forgot password flow with email verification message."""
    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        valid, message = validate_email(email)
        if not valid:
            flash(message, "danger")
            return render_template("login.html", show_forgot=True)

        user = User.query.filter_by(email=email).first()
        if user:
            flash(
                "If the email exists in our system, password reset instructions have been sent.",
                "info",
            )
        else:
            flash(
                "If the email exists in our system, password reset instructions have been sent.",
                "info",
            )
        return redirect(url_for("login"))

    return render_template("login.html", show_forgot=True)


@app.route("/profile", methods=["GET", "POST"])
@login_required
def profile():
    """User profile management."""
    user = User.query.get(session["user_id"])

    if request.method == "POST":
        name = request.form.get("name", "").strip()
        valid, message = validate_name(name)
        if not valid:
            flash(message, "danger")
            return render_template("profile.html", user=user)

        new_password = request.form.get("new_password", "")
        confirm_password = request.form.get("confirm_password", "")

        user.name = name
        if new_password:
            valid, message = validate_password(new_password)
            if not valid:
                flash(message, "danger")
                return render_template("profile.html", user=user)
            if new_password != confirm_password:
                flash("New passwords do not match.", "danger")
                return render_template("profile.html", user=user)
            user.set_password(new_password)

        db.session.commit()
        session["user_name"] = user.name
        flash("Profile updated successfully.", "success")
        return redirect(url_for("profile"))

    prediction_count = Prediction.query.filter_by(user_id=user.id).count()
    return render_template("profile.html", user=user, prediction_count=prediction_count)


@app.route("/dashboard")
@login_required
def dashboard():
    """User dashboard with statistics."""
    user_id = session["user_id"]
    predictions = Prediction.query.filter_by(user_id=user_id).order_by(Prediction.created_at.desc()).all()

    low_count = sum(1 for p in predictions if p.prediction == "Low Risk")
    medium_count = sum(1 for p in predictions if p.prediction == "Medium Risk")
    high_count = sum(1 for p in predictions if p.prediction == "High Risk")
    monthly_stats = get_monthly_statistics(predictions)

    return render_template(
        "dashboard.html",
        predictions=predictions[:10],
        total_predictions=len(predictions),
        low_count=low_count,
        medium_count=medium_count,
        high_count=high_count,
        monthly_stats=monthly_stats,
    )


@app.route("/predict", methods=["GET", "POST"])
@login_required
def predict_page():
    """Health risk prediction page."""
    result = None
    recommendation_sections = None

    if request.method == "POST":
        form_data = {
            "age": request.form.get("age"),
            "gender": request.form.get("gender"),
            "height": request.form.get("height"),
            "weight": request.form.get("weight"),
            "bmi": request.form.get("bmi"),
            "systolic_bp": request.form.get("systolic_bp"),
            "diastolic_bp": request.form.get("diastolic_bp"),
            "heart_rate": request.form.get("heart_rate"),
            "blood_sugar": request.form.get("blood_sugar"),
            "cholesterol": request.form.get("cholesterol"),
            "smoking": request.form.get("smoking"),
            "alcohol": request.form.get("alcohol"),
            "exercise_frequency": request.form.get("exercise_frequency"),
            "diet_quality": request.form.get("diet_quality"),
            "sleep_hours": request.form.get("sleep_hours"),
            "stress_level": request.form.get("stress_level"),
            "family_history": request.form.get("family_history"),
        }

        if not form_data["bmi"] and form_data["height"] and form_data["weight"]:
            form_data["bmi"] = str(calculate_bmi(float(form_data["weight"]), float(form_data["height"])))

        valid, errors = validate_prediction_form(form_data)
        if not valid:
            for error in errors:
                flash(error, "danger")
            return render_template("prediction.html", form_data=form_data)

        try:
            result = predictor.predict(form_data)
            recommendation_text, recommendation_sections = build_full_recommendation(
                result["prediction"], form_data
            )

            prediction_record = Prediction(
                user_id=session["user_id"],
                prediction=result["prediction"],
                probability=result["risk_percentage"],
                confidence=result["confidence"],
                recommendation=recommendation_text,
            )
            db.session.add(prediction_record)
            db.session.commit()

            result["prediction_id"] = prediction_record.id
            result["recommendation_sections"] = recommendation_sections
            flash("Prediction completed successfully.", "success")

        except Exception as exc:
            flash(f"Prediction failed: {str(exc)}", "danger")
            return render_template("prediction.html", form_data=form_data)

    return render_template(
        "prediction.html",
        result=result,
        recommendation_sections=recommendation_sections,
        form_data=request.form if request.method == "POST" else None,
    )


@app.route("/history")
@login_required
def history():
    """Prediction history for logged-in user."""
    predictions = (
        Prediction.query.filter_by(user_id=session["user_id"])
        .order_by(Prediction.created_at.desc())
        .all()
    )
    return render_template("history.html", predictions=predictions)


@app.route("/report/<int:prediction_id>")
@login_required
def download_report(prediction_id):
    """Generate and download PDF health report."""
    prediction = Prediction.query.get_or_404(prediction_id)
    if prediction.user_id != session["user_id"] and "admin_id" not in session:
        flash("Unauthorized access.", "danger")
        return redirect(url_for("history"))

    user = User.query.get(prediction.user_id)
    filename = generate_report_filename(user.name)
    filepath = os.path.join(Config.REPORTS_DIR, filename)

    doc = SimpleDocTemplate(filepath, pagesize=letter, rightMargin=50, leftMargin=50, topMargin=50, bottomMargin=50)
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle("TitleStyle", parent=styles["Heading1"], fontSize=20, textColor=colors.HexColor("#4e73df"))
    heading_style = ParagraphStyle("HeadingStyle", parent=styles["Heading2"], fontSize=14, textColor=colors.HexColor("#1cc88a"))
    body_style = styles["BodyText"]

    elements = [
        Paragraph("Health Risk Prediction Report", title_style),
        Spacer(1, 0.3 * inch),
        Paragraph(f"<b>Date:</b> {format_datetime(prediction.created_at)}", body_style),
        Spacer(1, 0.2 * inch),
        Paragraph("Patient Details", heading_style),
        Spacer(1, 0.1 * inch),
    ]

    patient_data = [
        ["Name", user.name],
        ["Email", user.email],
        ["Report Generated", datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")],
    ]
    patient_table = Table(patient_data, colWidths=[2 * inch, 4 * inch])
    patient_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (0, -1), colors.HexColor("#f8f9fc")),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
        ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
    ]))
    elements.extend([patient_table, Spacer(1, 0.3 * inch)])

    elements.append(Paragraph("Prediction Results", heading_style))
    elements.append(Spacer(1, 0.1 * inch))

    result_data = [
        ["Risk Level", prediction.prediction],
        ["Confidence Score", f"{prediction.confidence}%"],
        ["Risk Percentage", f"{prediction.probability}%"],
    ]
    result_table = Table(result_data, colWidths=[2 * inch, 4 * inch])
    result_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (0, -1), colors.HexColor("#f8f9fc")),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
        ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
    ]))
    elements.extend([result_table, Spacer(1, 0.3 * inch)])

    elements.append(Paragraph("Recommendations", heading_style))
    elements.append(Spacer(1, 0.1 * inch))
    for line in prediction.recommendation.split("\n"):
        if line.strip():
            elements.append(Paragraph(line.replace("- ", "&#8226; "), body_style))
            elements.append(Spacer(1, 0.05 * inch))

    doc.build(elements)
    return send_from_directory(Config.REPORTS_DIR, filename, as_attachment=True)


@app.route("/admin/login", methods=["GET", "POST"])
def admin_login():
    """Admin login page."""
    if "admin_id" in session:
        return redirect(url_for("admin_dashboard"))

    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")

        admin = Admin.query.filter_by(username=username).first()
        if admin and admin.check_password(password):
            session.clear()
            session["admin_id"] = admin.id
            session["admin_username"] = admin.username
            flash("Admin login successful.", "success")
            return redirect(url_for("admin_dashboard"))

        flash("Invalid admin credentials.", "danger")

    return render_template("admin.html", admin_login=True)


@app.route("/admin/logout")
def admin_logout():
    """Admin logout."""
    session.clear()
    flash("Admin logged out.", "info")
    return redirect(url_for("admin_login"))


@app.route("/admin/dashboard")
@admin_required
def admin_dashboard():
    """Admin dashboard with system-wide statistics."""
    total_users = User.query.count()
    predictions = Prediction.query.order_by(Prediction.created_at.desc()).all()
    total_predictions = len(predictions)
    low_count = sum(1 for p in predictions if p.prediction == "Low Risk")
    medium_count = sum(1 for p in predictions if p.prediction == "Medium Risk")
    high_count = sum(1 for p in predictions if p.prediction == "High Risk")
    feedbacks = Feedback.query.order_by(Feedback.created_at.desc()).limit(10).all()
    users = User.query.order_by(User.created_at.desc()).limit(10).all()
    monthly_stats = get_monthly_statistics(predictions)

    return render_template(
        "admin.html",
        admin_login=False,
        total_users=total_users,
        total_predictions=total_predictions,
        low_count=low_count,
        medium_count=medium_count,
        high_count=high_count,
        latest_predictions=predictions[:10],
        feedbacks=feedbacks,
        users=users,
        monthly_stats=monthly_stats,
    )


@app.route("/feedback", methods=["GET", "POST"])
@login_required
def feedback_page():
    """User feedback submission."""
    if request.method == "POST":
        feedback_text = request.form.get("feedback", "").strip()
        rating = request.form.get("rating", "")

        valid, message = validate_feedback(feedback_text, rating)
        if not valid:
            flash(message, "danger")
            return render_template("feedback.html")

        entry = Feedback(
            user_id=session["user_id"],
            feedback=feedback_text,
            rating=int(rating),
        )
        db.session.add(entry)
        db.session.commit()
        flash("Thank you for your feedback!", "success")
        return redirect(url_for("feedback_page"))

    user_feedbacks = (
        Feedback.query.filter_by(user_id=session["user_id"])
        .order_by(Feedback.created_at.desc())
        .all()
    )
    return render_template("feedback.html", user_feedbacks=user_feedbacks)


@app.route("/about")
def about():
    """About page."""
    return render_template("about.html")


@app.route("/contact", methods=["GET", "POST"])
def contact():
    """Contact page."""
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip()
        message = request.form.get("message", "").strip()

        valid, msg = validate_name(name)
        if not valid:
            flash(msg, "danger")
            return render_template("contact.html")

        valid, msg = validate_email(email)
        if not valid:
            flash(msg, "danger")
            return render_template("contact.html")

        if len(message) < 10:
            flash("Message must be at least 10 characters.", "danger")
            return render_template("contact.html")

        flash("Your message has been received. We will contact you soon.", "success")
        return redirect(url_for("contact"))

    return render_template("contact.html")


@app.route("/api/calculate-bmi", methods=["POST"])
@csrf.exempt
def api_calculate_bmi():
    """API endpoint for BMI calculation."""
    data = request.get_json(silent=True) or {}
    try:
        weight = float(data.get("weight", 0))
        height = float(data.get("height", 0))
        bmi = calculate_bmi(weight, height)
        return jsonify({"bmi": bmi})
    except (TypeError, ValueError):
        return jsonify({"error": "Invalid input"}), 400


@app.errorhandler(404)
def not_found_error(error):
    """Custom 404 page."""
    return render_template("404.html"), 404


@app.errorhandler(500)
def internal_error(error):
    """Custom 500 page."""
    db.session.rollback()
    return render_template("500.html"), 500


if __name__ == "__main__":
    ensure_project_ready()
    app.run(debug=True, host="0.0.0.0", port=5000, use_reloader=False)
