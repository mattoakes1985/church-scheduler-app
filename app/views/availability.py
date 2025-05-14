from flask import Blueprint, render_template, request, redirect, url_for
from datetime import datetime, timedelta
from app.extensions import db
from app.core.models import (
    Volunteer, Event, Team, Role,
    VolunteerTeamRole, VolunteerAvailability
)


availability_bp = Blueprint('availability', __name__, url_prefix='/availability')

@availability_bp.route("/", methods=["GET", "POST"])
def availability_page():
    # Pick a real volunteer from the DB for testing
    volunteer = Volunteer.query.first()
    if not volunteer:
        return "No volunteer available in the database."

    upcoming_events = Event.query.filter(Event.date >= datetime.today()).order_by(Event.date).all()

    # Get teams the volunteer is part of
    team_ids = [vtr.team_id for vtr in volunteer.volunteer_roles]
    teams = Team.query.filter(Team.id.in_(team_ids)).all()

    # Map team_id -> roles the volunteer is eligible for
    team_roles = {}
    for vtr in volunteer.volunteer_roles:
        team_roles.setdefault(vtr.team_id, []).append(vtr.role)

    submitted = VolunteerAvailability.query.filter_by(volunteer_id=volunteer.id).all()
    
    availability_map = {
        s.event_id: {"status": s.status, "team_id": s.team_id}
        for s in submitted
    }
    



    return render_template("volunteer/availability.html",
        volunteer=volunteer,
        events=upcoming_events,
        teams=teams,
        team_roles=team_roles,
        availability_map=availability_map
    )
