from flask import Blueprint, render_template
from flask_login import login_required

main = Blueprint('main', __name__)

@main.route('/')
def index():
    return render_template('index.html')

@main.route('/volunteer-portal')
@login_required
def volunteer_portal():
    return render_template('volunteer_portal.html')

@main.route("/login")
def login():
    return "<h1>Login page (coming soon)</h1>"

#