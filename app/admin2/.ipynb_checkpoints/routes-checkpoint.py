from flask import Blueprint, render_template, redirect, url_for, request, flash
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

@admin2_bp.route("/volunteers/add", methods=["GET", "POST"])
def add_volunteer():
    if request.method == "POST":
        name = request.form.get("name")
        email = request.form.get("email")
        is_admin = "is_admin" in request.form
        v = Volunteer(name=name, email=email, is_admin=is_admin)

        if name:
            v = Volunteer(name=name, email=email, is_lead=is_lead)
            db.session.add(v)
            db.session.commit()
            flash("Volunteer added!", "success")
            return redirect(url_for("admin2.volunteers"))
    return render_template("admin2/volunteer_form.html", action="Add")

@admin2_bp.route("/volunteers/edit/<int:id>", methods=["GET", "POST"])
def edit_volunteer(id):
    v = Volunteer.query.get_or_404(id)
    if request.method == "POST":
        v.name = request.form.get("name")
        v.email = request.form.get("email")
        v.v.is_admin = "is_admin" in request.form

        db.session.commit()
        flash("Volunteer updated!", "success")
        return redirect(url_for("admin2.volunteers"))
    return render_template("admin2/volunteer_form.html", volunteer=v, action="Edit")

@admin2_bp.route("/volunteers/delete/<int:id>", methods=["POST"])
def delete_volunteer(id):
    v = Volunteer.query.get_or_404(id)
    db.session.delete(v)
    db.session.commit()
    flash("Volunteer deleted.", "info")
    return redirect(url_for("admin2.volunteers"))
