from flask import Blueprint, render_template
from flask_login import current_user, login_required
from datetime import datetime, timedelta
from app.extensions import db
from app.core.models import Event, VolunteerAssignment, VolunteerAvailability

volunteer_dashboard_bp = Blueprint("volunteer_dashboard", __name__, url_prefix="/volunteer")

@volunteer_dashboard_bp.route("/dashboard")
@login_required
def dashboard():
    # Limit to 6 weeks from today
    now = datetime.now()
    six_weeks_later = now + timedelta(weeks=6)

    # Upcoming assignments
    upcoming_assignments = db.session.query(VolunteerAssignment).join(Event)\
        .filter(VolunteerAssignment.volunteer_id == current_user.id)\
        .filter(Event.date >= now, Event.date <= six_weeks_later)\
        .order_by(Event.date).all()

    # Availability reminders
    all_events = Event.query.filter(Event.date >= now, Event.date <= six_weeks_later).all()
    responded_event_ids = {
        a.event_id: a.status for a in VolunteerAvailability.query.filter_by(volunteer_id=current_user.id).all()
    }

    availability_needed = [
        event for event in all_events
        if event.id not in responded_event_ids or responded_event_ids[event.id] == "maybe"
    ]

    return render_template("volunteer/dashboard.html",
        upcoming_assignments=upcoming_assignments,
        availability_needed=availability_needed
    )
