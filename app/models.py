from datetime import datetime
from . import db
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), nullable=False, unique=True)
    email = db.Column(db.String(120), nullable=False, unique=True)
    password_hash = db.Column(db.String(128), nullable=False)
    phone_no = db.Column(db.String(15), nullable=True)
    date_joined = db.Column(db.DateTime, default=datetime.utcnow)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f'<User {self.username}>'

class UserInfo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    height = db.Column(db.Float, nullable=False)
    current_weight = db.Column(db.Float, nullable=False)
    goal_weight = db.Column(db.Float, nullable=False)
    time_frame = db.Column(db.Integer, nullable=False)  
    user = db.relationship('User', backref=db.backref('info', uselist=False))

    def __repr__(self):
        return f'<UserInfo {self.user_id}>'