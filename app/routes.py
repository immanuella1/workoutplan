from flask import (
    Blueprint,
    render_template,
    redirect,
    url_for,
    flash,
    request,
    jsonify,
)
from flask_login import login_user, logout_user, login_required, current_user
from app import db, login_manager
from app.models import User, DailyCheckIn, UserInfo, WeightEntry, Workouts
from app.forms.forms import (
    RegistrationForm,
    LoginForm,
    UserInfoForm,
    WeightEntryForm,
    UpdateUserInfoForm,
)
from app.apis.nutrition_api import nutrition_calculator
from app.apis.openapi_api import workoutRecommendation
from datetime import date, datetime, timedelta

bp = Blueprint("auth", __name__)

############# HELPER FUNCTIONS ################################################
def generate_workout_plan(goal, height, current_weight):
    workout_plan = workoutRecommendation(goal, height, current_weight)

    lines = workout_plan.split("\n")
    days = [
        "Monday",
        "Tuesday",
        "Wednesday",
        "Thursday",
        "Friday",
        "Saturday",
        "Sunday",
        "Nutrition Goals",
    ]
    workout_dict = {day: "" for day in days}

    current_day = None
    for line in lines:
        if any(day in line for day in days):
            current_day = next(day for day in days if day in line)
            workout_dict[current_day] += (
                line.split(f"{current_day}: ")[1] if ": " in line else ""
            )
        elif current_day:
            workout_dict[current_day] += f"\n{line.strip()}"

    return workout_dict


def save_workout_plan(user_id, workout_dict):
    new_workout = Workouts(
        user_id=user_id,
        monday=workout_dict.get("Monday", "").strip(),
        tuesday=workout_dict.get("Tuesday", "").strip(),
        wednesday=workout_dict.get("Wednesday", "").strip(),
        thursday=workout_dict.get("Thursday", "").strip(),
        friday=workout_dict.get("Friday", "").strip(),
        saturday=workout_dict.get("Saturday", "").strip(),
        sunday=workout_dict.get("Sunday", "").strip(),
        nutrition_goals=workout_dict.get("Nutrition Goals", "").strip(),
    )
    db.session.add(new_workout)
    db.session.commit()


def parse_workout_text(workout_text):
    lines = workout_text.split('-')
    formatted_lines = []
    for line in lines:
        if line.strip():
            parts = line.strip().split(':', 1)
            if len(parts) == 2:
                header, details = parts
                formatted_lines.append(f"<strong>{header.strip()}:</strong> {details.strip()}")
            else:
                formatted_lines.append(parts[0].strip())
    return '<br>'.join(formatted_lines)
####################################################################################

# HOME PAGE
@bp.route("/")
def index():
    if current_user.is_authenticated:
        last_entry = (
            WeightEntry.query.filter_by(user_id=current_user.id)
            .order_by(WeightEntry.date.desc())
            .first()
        )
        next_update = None
        if last_entry:
            next_update = last_entry.date + timedelta(weeks=2)
            today = datetime.utcnow().date()
            if today < next_update:
                next_update = next_update.strftime("%Y-%m-%d")
                
        workout_plan = Workouts.query.filter_by(user_id=current_user.id).first()
        if workout_plan:
            workout_plan.monday = parse_workout_text(workout_plan.monday)
            workout_plan.tuesday = parse_workout_text(workout_plan.tuesday)
            workout_plan.wednesday = parse_workout_text(workout_plan.wednesday)
            workout_plan.thursday = parse_workout_text(workout_plan.thursday)
            workout_plan.friday = parse_workout_text(workout_plan.friday)
            workout_plan.saturday = parse_workout_text(workout_plan.saturday)
            workout_plan.sunday = parse_workout_text(workout_plan.sunday)
            workout_plan.nutrition_goals = parse_workout_text(workout_plan.nutrition_goals)
        
        return render_template("index.html", next_update=next_update, workout_plan=workout_plan)
    else:
        return render_template("index.html")



# REGISTRATION ROUTE
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
            return redirect(url_for("auth.mandatory_update"))

        return redirect(url_for("auth.login"))
    return render_template("register.html", form=form)

# Mandatory route upon registration
@bp.route("/mandatory-update", methods=["GET", "POST"])
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
            goal=form.goal.data,
            time_frame=form.time_frame.data,
        )
        db.session.add(user_info)

        initial_weight_entry = WeightEntry(
            user_id=current_user.id, weight=form.current_weight.data
        )
        db.session.add(initial_weight_entry)

        workout_dict = generate_workout_plan(
            form.goal.data, form.height.data, form.current_weight.data
        )
        save_workout_plan(current_user.id, workout_dict)

        flash("Your information has been saved.")
        flash(workout_dict, "workout_plan")
        return redirect(url_for("auth.index"))

    return render_template("mandatory_update.html", form=form)

# LOGIN ROUTE
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

# LOGOUT BUTTON FUNCTIONALITY
@bp.route("/logout", methods=["POST"])
@login_required
def logout():
    logout_user()
    return redirect(url_for("auth.index"))

# DAILY CHECK IN ROUTE
@bp.route("/daily-checkin", methods=["GET", "POST"])
@login_required
def daily_checkin():
    today = date.today()
    existing_checkin = DailyCheckIn.query.filter_by(user_id=current_user.id, date=today).first()

    if request.method == "POST":
        did_workout = request.form.get("did_workout") == "on"
        food_log = request.form.get("food_log")
        nutrition_data = nutrition_calculator(food_log)

        try:
            if existing_checkin:
                existing_checkin.total_calories += nutrition_data.get("total_calories", 0)
                existing_checkin.total_protein += nutrition_data.get("total_protein", 0)
                existing_checkin.total_sugars += nutrition_data.get("total_sugars", 0)
                existing_checkin.total_sodium += nutrition_data.get("total_sodium", 0)

                if not existing_checkin.did_workout and did_workout:
                    existing_checkin.did_workout = True
                    existing_checkin.points_earned += 50
                    current_user.add_points(50)
                    flash("You have marked your workout and earned 50 points.")

                flash("Your food log has been updated.")
            else:
                checkin = DailyCheckIn(
                    user_id=current_user.id,
                    did_workout=did_workout,
                    total_calories=nutrition_data.get("total_calories", 0),
                    total_protein=nutrition_data.get("total_protein", 0),
                    total_sugars=nutrition_data.get("total_sugars", 0),
                    total_sodium=nutrition_data.get("total_sodium", 0),
                    points_earned=50 if did_workout else 0
                )

                if did_workout:
                    current_user.add_points(50)
                    flash("Check-in successful! You earned 50 points.")
                else:
                    flash("Check-in successful!")

                db.session.add(checkin)

            db.session.commit()
            return redirect(url_for("auth.daily_checkin"))
        except Exception as e:
            db.session.rollback()
            flash(f"An error occurred: {e}")

    return render_template("daily_checkin.html", existing_checkin=existing_checkin)


# Route to check in with daily work out
@bp.route("/checkin-history")
@login_required
def checkin_history():
    checkins = DailyCheckIn.query.filter_by(user_id=current_user.id).order_by(DailyCheckIn.date.desc()).all()
    user_info = UserInfo.query.filter_by(user_id=current_user.id).first()
    return render_template("checkin_history.html", checkins=checkins, total_points=user_info.points_earned if user_info else 0)



# Display workouts
@bp.route("/workout")
@login_required
def workout():
    workout_plan = Workouts.query.filter_by(user_id=current_user.id).first()
    if workout_plan:
        workout_plan.monday = parse_workout_text(workout_plan.monday)
        workout_plan.tuesday = parse_workout_text(workout_plan.tuesday)
        workout_plan.wednesday = parse_workout_text(workout_plan.wednesday)
        workout_plan.thursday = parse_workout_text(workout_plan.thursday)
        workout_plan.friday = parse_workout_text(workout_plan.friday)
        workout_plan.saturday = parse_workout_text(workout_plan.saturday)
        workout_plan.sunday = parse_workout_text(workout_plan.sunday)
        workout_plan.nutrition_goals = parse_workout_text(workout_plan.nutrition_goals)
    return render_template("workout.html", workout_plan=workout_plan)


# Update weight route
@bp.route("/weight-update", methods=["GET", "POST"])
@login_required
def weight_update():
    form = WeightEntryForm()
    last_entry = (
        WeightEntry.query.filter_by(user_id=current_user.id)
        .order_by(WeightEntry.date.desc())
        .first()
    )
    next_update = None
    if last_entry:
        next_update = last_entry.date + timedelta(weeks=2)
        today = datetime.utcnow().date()
        if today < next_update:
            next_update = next_update.strftime("%Y-%m-%d")
            return render_template(
                "weight_update.html", form=None, next_update=next_update
            )

    if form.validate_on_submit():
        weight_entry = WeightEntry(user_id=current_user.id, weight=form.weight.data)
        db.session.add(weight_entry)
        db.session.commit()
        flash("Your weight has been updated!")
        return redirect(url_for("auth.weight_history"))

    return render_template("weight_update.html", form=form, next_update=None)


# Used to create graph
@bp.route("/weight-history-data")
@login_required
def weight_history_data():
    weight_entries = (
        WeightEntry.query.filter_by(user_id=current_user.id)
        .order_by(WeightEntry.date.asc())
        .all()
    )
    data = {
        "dates": [entry.date.strftime("%Y-%m-%d") for entry in weight_entries],
        "weights": [entry.weight for entry in weight_entries],
    }
    return jsonify(data)


# Route to check weight history
@bp.route("/weight-history")
@login_required
def weight_history():
    next_update = None
    weight_entries = (
        WeightEntry.query.filter_by(user_id=current_user.id)
        .order_by(WeightEntry.date.desc())
        .all()
    )
    if weight_entries:
        last_entry = weight_entries[0]
        next_update = last_entry.date + timedelta(weeks=2)
        today = datetime.today().date()
        if today < next_update:
            next_update = next_update.strftime("%Y-%m-%d")
        else:
            next_update = None

    return render_template("weight_history.html", next_update=next_update)


# Route to update goals
@bp.route("/update_info", methods=["GET", "POST"])
@login_required
def update_info():
    user_info = UserInfo.query.filter_by(user_id=current_user.id).first()
    if not user_info:
        flash("User information not found.")
        return redirect(url_for("auth.index"))

    form = UpdateUserInfoForm(obj=user_info)
    if form.validate_on_submit():
        user_info.goal = form.goal.data
        user_info.time_frame = form.time_frame.data

        old_workout = Workouts.query.filter_by(user_id=current_user.id).first()
        if old_workout:
            db.session.delete(old_workout)

        workout_dict = generate_workout_plan(
            form.goal.data, user_info.height, user_info.current_weight
        )
        save_workout_plan(current_user.id, workout_dict)

        db.session.commit()
        flash(
            "Your information has been updated and a new workout plan has been generated."
        )
        return redirect(url_for("auth.index"))

    return render_template("update_info.html", form=form)


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))
