from flask import Blueprint, render_template
from app.core.models import Volunteer
from app.extensions import db

admin2_bp = Blueprint("admin2", __name__, url_prefix="/admin2")

@admin2_bp.route("/")
def index():
    return render_template("admin2/index.html")

@admin2_bp.route("/volunteers")
def volunteers():
    volunteers = db.session.query(Volunteer).all()
    return render_template("admin2/volunteers.html", volunteers=volunteers)
