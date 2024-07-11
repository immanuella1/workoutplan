from datetime import datetime, date, timedelta
from . import db
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text
from alembic import op
import sqlalchemy as sa
from sqlalchemy import text


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), nullable=False, unique=True)
    email = db.Column(db.String(120), nullable=False, unique=True)
    password_hash = db.Column(db.String(128), nullable=False)
    phone_no = db.Column(db.String(15), nullable=True)
    date_joined = db.Column(db.DateTime, default=datetime.utcnow)
    points = db.Column(db.Integer, default=0, nullable=True)

    # Put nullable as true insead of false

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def add_points(self, points):
        self.points += points

    @property
    def level(self):
        if self.points >= 2000:
            return "Expert"
        elif self.points >= 1800:
            return "Pro"
        elif self.points >= 1200:
            return "Intermediate"
        elif self.points >= 200:
            return "Novice"
        else:
            return "Beginner"

    def __repr__(self):
        return f"<User {self.username}>"


class UserInfo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    height = db.Column(db.Float, nullable=False)
    current_weight = db.Column(db.Float, nullable=False)
    goal = db.Column(db.String(255), nullable=False)
    time_frame = db.Column(db.Integer, nullable=False)
    user = db.relationship("User", backref=db.backref("info", uselist=False))

    def __repr__(self):
        return f"<UserInfo {self.user_id}>"


class DailyCheckIn(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, default=date.today, nullable=False)
    did_workout = db.Column(db.Boolean, default=False, nullable=False)
    total_calories = db.Column(db.Float, nullable=True)
    total_protein = db.Column(db.Float, nullable=True)
    total_sugars = db.Column(db.Float, nullable=True)
    total_sodium = db.Column(db.Float, nullable=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    user = db.relationship("User", backref=db.backref("daily_checkins", lazy=True))

    __table_args__ = (
        db.UniqueConstraint("user_id", "date", name="unique_user_date_checkin"),
    )

    def __repr__(self):
        return f"<DailyCheckIn {self.date} for User {self.user_id}>"


class WeightEntry(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    weight = db.Column(db.Float, nullable=False)
    date = db.Column(db.Date, default=datetime.today, nullable=False)
    user = db.relationship("User", backref=db.backref("weight_entries", lazy=True))

    def __repr__(self):
        return f"<WeightEntry {self.user_id} - {self.date}>"

class Workouts(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    monday = db.Column(db.String(500), nullable=False)
    tuesday = db.Column(db.String(500), nullable=False)
    wednesday = db.Column(db.String(500), nullable=False)
    thursday = db.Column(db.String(500), nullable=False)
    friday = db.Column(db.String(500), nullable=False)
    saturday = db.Column(db.String(500), nullable=False)
    sunday = db.Column(db.String(500), nullable=False)
    nutrition_goals = db.Column(db.String(500), nullable=False)

    user = db.relationship("User", backref=db.backref("workouts", lazy=True))
    
    def __repr__(self):
        return f"<Workouts {self.user_id}>"