from flask import Blueprint, render_template
from flask_login import login_required
from datetime import datetime
from flask import redirect, url_for, flash
from flask_login import current_user


main = Blueprint('main', __name__)

@main.route('/')
def index():
    return render_template('index.html')

@main.route('/volunteer-portal')
#@login_required
def volunteer_portal():
    return render_template('volunteer_portal.html', current_year=datetime.now().year)

@main.route("/login")
def login():
    return "<h1>Login page (coming soon)</h1>"

def admin_tools():
    if not current_user.is_authenticated or not current_user.is_admin:
        flash("Access denied.", "error")
        return redirect(url_for("main.index"))
    return render_template("admin_tools.html")
