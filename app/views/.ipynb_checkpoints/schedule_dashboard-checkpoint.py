from flask import Blueprint, render_template, request
from sqlalchemy import extract, func, and_
from app.extensions import db
from app.core.models import (
    Event, Role, Volunteer, VolunteerAvailability,
    EventTeamRequirement, VolunteerAssignment, TemplateTeamRole
)

schedule_dashboard_bp = Blueprint('schedule_dashboard', __name__, url_prefix='/schedule')

@schedule_dashboard_bp.route("/dashboard")
def schedule_dashboard():
    selected_year = request.args.get("year", type=int)
    selected_month = request.args.get("month", type=int)

    if not selected_year or not selected_month:
        return render_template("schedule/dashboard.html", events=[], roles=[], assignment_matrix={}, volunteer_counts={}, no_availability=[], unfilled_roles=[], selected_year=selected_year, selected_month_name="")

    # Get all events in the month
    events = Event.query.filter(
        and_(
            Event.archived_at == None,
            extract("year", Event.date) == selected_year,
            extract("month", Event.date) == selected_month
        )
    ).order_by(Event.date).all()

    event_ids = [e.id for e in events]

    # Load role position mapping from template ID 3
    position_lookup = {
        (ttr.team_id, ttr.role_id): ttr.position
        for ttr in db.session.query(TemplateTeamRole)
        .filter(TemplateTeamRole.template_id == 3)
    }

    # Get all roles used in those events
    role_set = set()
    for eid in event_ids:
        reqs = EventTeamRequirement.query.filter_by(event_id=eid).all()
        for req in reqs:
            role_set.add((req.team_id, req.role_id, req.role))
    roles = sorted(
        [r[2] for r in role_set],
        key=lambda r: (
            position_lookup.get((next((t for t, rid, ro in role_set if ro.id == r.id), None), r.id), 9999),
            r.name
        )
    )

    # Get all assignments
    assignments = VolunteerAssignment.query.filter(
        VolunteerAssignment.event_id.in_(event_ids)
    ).all()

    assignment_matrix = {}
    volunteer_counts = {}
    for a in assignments:
        assignment_matrix[(a.event_id, a.role_id)] = a.volunteer
        volunteer_counts[a.volunteer] = volunteer_counts.get(a.volunteer, 0) + 1

    # Get volunteers who have submitted availability
    available_volunteers = db.session.query(VolunteerAvailability.volunteer_id).filter(
        VolunteerAvailability.event_id.in_(event_ids)
    ).distinct().all()
    available_ids = {v[0] for v in available_volunteers}

    all_volunteers = Volunteer.query.all()
    no_availability = [v for v in all_volunteers if v.id not in available_ids]

    # Find unfilled roles
    unfilled_roles = []
    for e in events:
        reqs = EventTeamRequirement.query.filter_by(event_id=e.id).all()
        for req in reqs:
            key = (e.id, req.role_id)
            if key not in assignment_matrix:
                unfilled_roles.append((e, req.role))

    month_names = [
        "January", "February", "March", "April", "May", "June",
        "July", "August", "September", "October", "November", "December"
    ]
    selected_month_name = month_names[selected_month - 1]

    return render_template("schedule/dashboard.html",
        events=events,
        roles=roles,
        assignment_matrix=assignment_matrix,
        volunteer_counts=volunteer_counts,
        no_availability=no_availability,
        unfilled_roles=unfilled_roles,
        selected_year=selected_year,
        selected_month_name=selected_month_name
    )
