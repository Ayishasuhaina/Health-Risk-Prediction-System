"""Database models and initialization."""

from datetime import datetime

from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import check_password_hash, generate_password_hash

db = SQLAlchemy()


class User(db.Model):
    """Registered application user."""

    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password = db.Column(db.String(256), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    predictions = db.relationship("Prediction", backref="user", lazy=True, cascade="all, delete-orphan")
    feedbacks = db.relationship("Feedback", backref="user", lazy=True, cascade="all, delete-orphan")

    def set_password(self, raw_password):
        """Hash and store user password."""
        self.password = generate_password_hash(raw_password)

    def check_password(self, raw_password):
        """Verify user password."""
        return check_password_hash(self.password, raw_password)


class Prediction(db.Model):
    """Stored health risk prediction."""

    __tablename__ = "predictions"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    prediction = db.Column(db.String(50), nullable=False)
    probability = db.Column(db.Float, nullable=False)
    confidence = db.Column(db.Float, nullable=False)
    recommendation = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class Admin(db.Model):
    """Administrator account."""

    __tablename__ = "admin"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(256), nullable=False)

    def set_password(self, raw_password):
        """Hash and store admin password."""
        self.password = generate_password_hash(raw_password)

    def check_password(self, raw_password):
        """Verify admin password."""
        return check_password_hash(self.password, raw_password)


class Feedback(db.Model):
    """User feedback entry."""

    __tablename__ = "feedback"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    feedback = db.Column(db.Text, nullable=False)
    rating = db.Column(db.Integer, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


def init_db(app, default_admin_username, default_admin_password):
    """Create tables and default admin user."""
    with app.app_context():
        db.create_all()
        admin = Admin.query.filter_by(username=default_admin_username).first()
        if not admin:
            admin = Admin(username=default_admin_username)
            admin.set_password(default_admin_password)
            db.session.add(admin)
            db.session.commit()
