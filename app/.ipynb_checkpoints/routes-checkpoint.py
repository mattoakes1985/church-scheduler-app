from flask import Blueprint, render_template
from flask_login import login_required
from datetime import datetime
from flask import redirect, url_for, flash
from flask_login import current_user
from app.decorators import admin_required


main = Blueprint('main', __name__)

@main.route('/')
def index():
    return render_template('index.html')

@main.route('/volunteer-portal')
@login_required


def admin_tools():
    if not current_user.is_authenticated or not current_user.is_admin:
        flash("Access denied.", "error")
        return redirect(url_for("main.index"))
    return render_template("admin_tools.html")

@main.route("/schedule/")
def schedule_volunteers():
    return render_template("schedule.html")

@main.route("/event-admin")
@admin_required
def event_admin():
    return render_template("admin/event_admin.html")


@main.route("/worship-lead")
def redirect_to_worship_planning():
    return redirect(url_for("worship_planning.planning"))

devtools_bp = Blueprint("devtools", __name__, url_prefix="/dev")

@devtools_bp.route("/run-migrations")
def run_migrations():
    try:
        upgrade()
        return "✅ Migrations applied successfully."
    except Exception as e:
        return f"❌ Migration error: {e}", 500