from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from app import db, login_manager
from app.models import User, DailyCheckIn, UserInfo
from app.forms.forms import RegistrationForm, LoginForm, UserInfoForm
from app.apis.nutrition_api import nutrition_calculator
from app.apis.openapi_api import *
from datetime import date
import openai
import os

bp = Blueprint("auth", __name__)

@bp.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("auth.index"))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(
            username=form.username.data,
            email=form.email.data,
            phone_no=form.phone_no.data,
        )
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        login_user(user)
        if not UserInfo.query.filter_by(user_id=user.id).first():
            return redirect(url_for('auth.mandatory_update'))
        
        return redirect(url_for("auth.login"))
    return render_template("register.html", form=form)


@bp.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("auth.index"))
    form = LoginForm()

    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash("Invalid username or password")
            return redirect(url_for("auth.login"))
        login_user(user, remember=form.remember_me.data)

        if not UserInfo.query.filter_by(user_id=user.id).first():
            return redirect(url_for("auth.mandatory_update"))

        return redirect(url_for("auth.index"))

    return render_template("login.html", form=form)


@bp.route("/logout", methods=["POST"])
@login_required
def logout():
    logout_user()
    return redirect(url_for("auth.index"))


@bp.route("/")
def index():
    return render_template("index.html")


"""
@bp.route("/nutrition", methods=['GET', 'POST'])
def nutrition():
    nutrition_data = None
    if request.method == 'POST':
        query = request.form.get('query')
        if query:
            nutrition_data = nutrition_calculator(query)
    return render_template('nutrition.html', nutrition_data=nutrition_data)
    
    Initially used for testing
"""


@bp.route("/daily-checkin", methods=["GET", "POST"])
@login_required
def daily_checkin():
    today = date.today()
    existing_checkin = DailyCheckIn.query.filter_by(
        user_id=current_user.id, date=today
    ).first()

    if request.method == "POST":
        if existing_checkin:
            flash("You have already checked in today.")
        else:
            did_workout = request.form.get("did_workout") == "on"
            food_log = request.form.get("food_log")

            nutrition_data = nutrition_calculator(food_log)

            try:
                checkin = DailyCheckIn(
                    user_id=current_user.id,
                    did_workout=did_workout,
                    total_calories=nutrition_data.get("total_calories"),
                    total_protein=nutrition_data.get("total_protein"),
                    total_sugars=nutrition_data.get("total_sugars"),
                    total_sodium=nutrition_data.get("total_sodium"),
                )

                db.session.add(checkin)
                db.session.commit()
                flash("Check-in successful!")
                return redirect(url_for("auth.checkin_history"))
            except Exception as e:
                db.session.rollback()
                flash(f"An error occurred: {e}")

    return render_template("daily_checkin.html", existing_checkin=existing_checkin)


@bp.route("/checkin-history")
@login_required
def checkin_history():
    checkins = DailyCheckIn.query.filter_by(user_id=current_user.id).all()
    return render_template("checkin_history.html", checkins=checkins)


@bp.route("/mandatory-update", methods=["GET", "POST"])
@bp.route("/mandatory-update")
@login_required
def mandatory_update():
    if UserInfo.query.filter_by(user_id=current_user.id).first():
        return redirect(url_for("auth.index"))

    form = UserInfoForm()
    if form.validate_on_submit():
        user_info = UserInfo(
            user_id=current_user.id,
            height=form.height.data,
            current_weight=form.current_weight.data,
            goal=form.goal.data,  # Updated field
            time_frame=form.time_frame.data,
        )
        db.session.add(user_info)
        db.session.commit()
        
        recommendation = workoutRecomendation(form.goal.data)
        
        flash("Your information has been saved and your workout plan has been generated.")
        return redirect(url_for("auth.index"))

    return render_template("mandatory_update.html", form=form)


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))
