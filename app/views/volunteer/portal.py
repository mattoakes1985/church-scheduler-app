# app/views/volunteer/portal.py

from flask import Blueprint, render_template
from flask_login import login_required, current_user
from datetime import datetime, timedelta
from app.core.models import (
    Event, EventTeamRequirement, VolunteerAvailability,
    VolunteerAssignment
)
from app.extensions import db

volunteer_portal_bp = Blueprint("volunteer_portal", __name__)

@volunteer_portal_bp.route("/volunteer-portal")
@login_required
def volunteer_portal():
    today = datetime.today().date()
    in_two_months = today + timedelta(days=60)
    three_months_ago = today - timedelta(days=90)

    team_ids = [vtr.team_id for vtr in current_user.volunteer_roles]


    upcoming_event_ids = (
        db.session.query(Event.id)
        .join(EventTeamRequirement)
        .filter(
            Event.date >= today,
            Event.date <= in_two_months,
            EventTeamRequirement.team_id.in_(team_ids),
            Event.archived_at.is_(None)
        )
        .distinct()
        .all()
    )
    upcoming_event_ids = [e.id for e in upcoming_event_ids]

    submitted_ids = {
        r.event_id for r in db.session.query(VolunteerAvailability.event_id)
        .filter(
            VolunteerAvailability.volunteer_id == current_user.id,
            VolunteerAvailability.event_id.in_(upcoming_event_ids)
        ).all()
    }

    availability_needed_count = len([eid for eid in upcoming_event_ids if eid not in submitted_ids])

    upcoming_serving_count = db.session.query(VolunteerAssignment).join(Event).filter(
        VolunteerAssignment.volunteer_id == current_user.id,
        Event.date >= today,
        Event.date <= in_two_months,
        Event.archived_at.is_(None)
    ).count()

    past_serving_count = db.session.query(VolunteerAssignment).join(Event).filter(
        VolunteerAssignment.volunteer_id == current_user.id,
        Event.date >= three_months_ago,
        Event.date < today,
        Event.archived_at.is_(None)
    ).count()

    return render_template(
        "volunteer_portal.html",
        current_year=datetime.now().year,
        availability_needed_count=availability_needed_count,
        upcoming_serving_count=upcoming_serving_count,
        past_serving_count=past_serving_count
    )
