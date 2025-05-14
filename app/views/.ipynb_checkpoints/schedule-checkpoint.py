from flask import Blueprint, render_template, request, redirect, url_for
from sqlalchemy import extract
from app.extensions import db
from app.core.models import (
    Event, Team, Role, Volunteer, VolunteerAvailability,
    EventTeamRequirement, VolunteerTeamRole, VolunteerAssignment
)

schedule_bp = Blueprint('schedule', __name__, url_prefix='/schedule')

@schedule_bp.route("/", methods=["GET", "POST"])
def schedule_page():
    selected_event_id = request.values.get("event_id", type=int)
    selected_team_id = request.values.get("team_id", type=int)
    selected_year = request.values.get("year", type=int)
    selected_month = request.values.get("month", type=int)

    years = db.session.query(extract('year', Event.date)).join(EventTeamRequirement).distinct().order_by(extract('year', Event.date).desc()).all()

    months = []
    events = []
    if selected_year:
        month_query = db.session.query(extract('month', Event.date)).join(EventTeamRequirement).filter(extract('year', Event.date) == selected_year).distinct().order_by(extract('month', Event.date))
        month_values = month_query.all()
        month_names = [
            (1, "January"), (2, "February"), (3, "March"), (4, "April"),
            (5, "May"), (6, "June"), (7, "July"), (8, "August"),
            (9, "September"), (10, "October"), (11, "November"), (12, "December")
        ]
        months = [m for m in month_names if (m[0],) in month_values]

        if selected_month:
            events = db.session.query(Event).join(EventTeamRequirement).filter(
                extract('year', Event.date) == selected_year,
                extract('month', Event.date) == selected_month
            ).order_by(Event.date.desc()).all()

    teams = []
    requirements = []
    eligible_volunteers = {}
    current_assignments = {}

    if selected_event_id:
        teams = db.session.query(Team).join(EventTeamRequirement)
        teams = teams.filter(EventTeamRequirement.event_id == selected_event_id).distinct().all()

    if selected_event_id and selected_team_id:
        available_ids = db.session.query(VolunteerAvailability.volunteer_id)
        available_ids = available_ids.filter_by(event_id=selected_event_id).subquery()

        requirements = EventTeamRequirement.query.filter_by(
            event_id=selected_event_id,
            team_id=selected_team_id
        ).all()

        for req in requirements:
            eligible = db.session.query(Volunteer).join(VolunteerTeamRole).filter(
                Volunteer.id.in_(available_ids),
                VolunteerTeamRole.team_id == selected_team_id,
                VolunteerTeamRole.role_id == req.role_id
            ).all()
            eligible_volunteers[req.role_id] = eligible

            assignment = VolunteerAssignment.query.filter_by(
                event_id=selected_event_id,
                team_id=selected_team_id,
                role_id=req.role_id
            ).first()
            current_assignments[req.role_id] = assignment.volunteer_id if assignment else None

    if request.method == "POST":
        for req in requirements:
            field = f"assignment_{req.role_id}"
            vol_id = request.form.get(field, type=int)

            existing = VolunteerAssignment.query.filter_by(
                event_id=selected_event_id,
                team_id=selected_team_id,
                role_id=req.role_id
            ).first()

            if vol_id:
                if existing:
                    existing.volunteer_id = vol_id
                else:
                    db.session.add(VolunteerAssignment(
                        event_id=selected_event_id,
                        team_id=selected_team_id,
                        role_id=req.role_id,
                        volunteer_id=vol_id
                    ))
            elif existing:
                db.session.delete(existing)

        db.session.commit()
        return redirect(url_for("schedule.schedule_page", event_id=selected_event_id, team_id=selected_team_id, year=selected_year, month=selected_month))

    return render_template(
        "schedule.html",
        events=events,
        teams=teams,
        requirements=requirements,
        eligible_volunteers=eligible_volunteers,
        current_assignments=current_assignments,
        selected_event_id=selected_event_id,
        selected_team_id=selected_team_id,
        years=years,
        months=months,
        selected_year=selected_year,
        selected_month=selected_month
    )


@schedule_bp.route("/months")
def load_months():
    year = request.args.get("year", type=int)
    months = []
    if year:
        month_query = db.session.query(extract('month', Event.date)).join(EventTeamRequirement).filter(
            extract('year', Event.date) == year
        ).distinct().order_by(extract('month', Event.date))
        month_values = month_query.all()
        month_names = [
            (1, "January"), (2, "February"), (3, "March"), (4, "April"),
            (5, "May"), (6, "June"), (7, "July"), (8, "August"),
            (9, "September"), (10, "October"), (11, "November"), (12, "December")
        ]
        months = [m for m in month_names if (m[0],) in month_values]

    return render_template("schedule/_months_select.html", months=months, selected_month=None)


@schedule_bp.route("/events")
def load_events():
    year = request.args.get("year", type=int)
    month = request.args.get("month", type=int)
    events = []
    if year and month:
        events = db.session.query(Event).join(EventTeamRequirement).filter(
            extract('year', Event.date) == year,
            extract('month', Event.date) == month
        ).order_by(Event.date.desc()).all()

    return render_template("schedule/_events_select.html", events=events, selected_event_id=None)
