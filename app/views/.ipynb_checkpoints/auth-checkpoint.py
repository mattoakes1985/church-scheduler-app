from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required
from app.extensions import db, login_manager
from app.core.models import Volunteer
from werkzeug.security import check_password_hash
from werkzeug.security import generate_password_hash
from flask_mail import Message
from app.extensions import mail  # make sure mail is initialized

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')

@login_manager.user_loader
def load_user(user_id):
    return Volunteer.query.get(int(user_id))

@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")
        user = Volunteer.query.filter_by(email=email).first()

        if user and user.password_hash and check_password_hash(user.password_hash, password):
            login_user(user)
            flash("Logged in successfully.", "success")
            return redirect(url_for("volunteer_portal.volunteer_portal"))


        flash("Invalid email or password.", "danger")

    return render_template("auth/login.html")

@auth_bp.route("/logout", methods=["POST"])
@login_required
def logout():
    logout_user()
    flash("You have been logged out.", "info")
    return redirect(url_for("auth.login"))



@auth_bp.route("/forgot-password", methods=["GET", "POST"])
def forgot_password():
    if request.method == "POST":
        email = request.form.get("email").strip().lower()
        user = Volunteer.query.filter_by(email=email).first()

        if user:
            token = user.get_reset_token()
            reset_url = url_for("auth.reset_password_token", token=token, _external=True)

            msg = Message("Password Reset Request", recipients=[email])
            msg.body = f"""Hello {user.name},

To reset your password, click the following link:
{reset_url}

If you did not request this, simply ignore this email.

- Church Scheduler Team
"""
            try:
                mail.send(msg)
                print("[DEBUG] Email sent successfully.")
            except Exception as e:
                print("[ERROR] Failed to send email:", e)

        flash("If your email is registered, you'll receive a password reset link.", "info")
        return redirect(url_for("auth.login"))

    return render_template("auth/forgot_password.html")



@auth_bp.route("/reset-password/<token>", methods=["GET", "POST"])
def reset_password_token(token):
    user = Volunteer.verify_reset_token(token)
    if not user:
        flash("That reset link is invalid or expired.", "danger")
        return redirect(url_for("auth.forgot_password"))

    if request.method == "POST":
        new_pw = request.form.get("password")
        confirm_pw = request.form.get("confirm_password")
        if new_pw != confirm_pw:
            flash("Passwords do not match.", "danger")
            return redirect(request.url)
        user.password_hash = generate_password_hash(new_pw)
        db.session.commit()
        flash("Password updated. You can now log in.", "success")
        return redirect(url_for("auth.login"))

    return render_template("auth/reset_password.html", volunteer=user)
