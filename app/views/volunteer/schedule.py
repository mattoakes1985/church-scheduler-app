from flask import Blueprint, render_template, request
from flask_login import login_required
from sqlalchemy import extract
from app.extensions import db
from app.core.models import Team, Event, Role, VolunteerAssignment, EventTeamRequirement

volunteer_schedule_bp = Blueprint("volunteer_schedule", __name__, url_prefix="/volunteer")

@volunteer_schedule_bp.route("/schedule")
@login_required
def schedule():
    selected_team_id = request.args.get("team_id", type=int)

    teams = Team.query.order_by(Team.name).all()

    selected_team = Team.query.get(selected_team_id) if selected_team_id else None

    # Default to current month/year
    from datetime import datetime
    now = datetime.now()
    selected_year = now.year
    selected_month = now.month

    events = Event.query.filter(
        extract("year", Event.date) == selected_year,
        extract("month", Event.date) == selected_month
    ).order_by(Event.date).all()

    event_ids = [e.id for e in events]

    roles = []
    assignment_matrix = {}
    if selected_team:
        roles = db.session.query(Role).join(EventTeamRequirement)\
            .filter(EventTeamRequirement.event_id.in_(event_ids))\
            .filter(EventTeamRequirement.team_id == selected_team_id)\
            .distinct().all()

        assignments = VolunteerAssignment.query.filter(
            VolunteerAssignment.event_id.in_(event_ids),
            VolunteerAssignment.team_id == selected_team_id
        ).all()

        for a in assignments:
            assignment_matrix[(a.event_id, a.role_id)] = a.volunteer

    return render_template("volunteer/schedule.html",
        teams=teams,
        selected_team=selected_team,
        events=events,
        roles=roles,
        assignment_matrix=assignment_matrix
    )
