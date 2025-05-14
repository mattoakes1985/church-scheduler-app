from flask import Blueprint, render_template, request, redirect, url_for
from app.extensions import db
from sqlalchemy import extract
from app.core.models import (
    Event, Team, Role, Volunteer, VolunteerAvailability,
    EventTeamRequirement, VolunteerTeamRole, VolunteerAssignment
)

schedule_bp = Blueprint('schedule', __name__, url_prefix='/schedule')

@schedule_bp.route("/", methods=["GET", "POST"])
def schedule_page():
    selected_year = request.values.get("year", type=int)
    selected_month = request.values.get("month", type=int)
    selected_team_id = request.values.get("team_id", type=int)

    years = db.session.query(extract('year', Event.date)).distinct().order_by(extract('year', Event.date).desc()).all()
    months = []
    events = []
    teams = []
    event_cards = {}

    if selected_year:
        months_query = db.session.query(extract('month', Event.date))\
            .filter(extract('year', Event.date) == selected_year).distinct()
        month_nums = [m[0] for m in months_query]
        months = [(m, [
            "January", "February", "March", "April", "May", "June",
            "July", "August", "September", "October", "November", "December"
        ][m - 1]) for m in month_nums]

    if selected_year and selected_month:
        events = Event.query.filter(
            extract('year', Event.date) == selected_year,
            extract('month', Event.date) == selected_month
        ).order_by(Event.date).all()

        event_ids = [e.id for e in events]

        if event_ids:
            teams = db.session.query(Team).join(EventTeamRequirement)\
                .filter(EventTeamRequirement.event_id.in_(event_ids))\
                .distinct().all()

        if selected_team_id:
            for event in events:
                requirements = EventTeamRequirement.query.filter_by(
                    event_id=event.id,
                    team_id=selected_team_id
                ).all()

                available_ids = db.session.query(VolunteerAvailability.volunteer_id)\
                    .filter_by(event_id=event.id).subquery()

                eligible = {}
                assignments = {}

                for req in requirements:
                    eligible[req.role_id] = db.session.query(Volunteer).join(VolunteerTeamRole).filter(
                        Volunteer.id.in_(available_ids),
                        VolunteerTeamRole.team_id == selected_team_id,
                        VolunteerTeamRole.role_id == req.role_id
                    ).all()

                    assigned = VolunteerAssignment.query.filter_by(
                        event_id=event.id,
                        team_id=selected_team_id,
                        role_id=req.role_id
                    ).first()

                    if assigned:
                        assignments[req.role_id] = assigned.volunteer_id
                

                event_cards[event.id] = {
                    "requirements": requirements,
                    "eligible": eligible,
                    "assignments": assignments
                }

    if request.method == "POST":
        # Save logic for multi-event cards
        for key, val in request.form.items():
            if key.startswith("assignment_"):
                parts = key.split("_")
                if len(parts) == 3:
                    event_id, role_id = int(parts[1]), int(parts[2])
                    volunteer_id = int(val) if val else None

                    existing = VolunteerAssignment.query.filter_by(
                        event_id=event_id,
                        team_id=selected_team_id,
                        role_id=role_id
                    ).first()

                    if volunteer_id:
                        if existing:
                            existing.volunteer_id = volunteer_id
                        else:
                            db.session.add(VolunteerAssignment(
                                event_id=event_id,
                                team_id=selected_team_id,
                                role_id=role_id,
                                volunteer_id=volunteer_id
                            ))
                    elif existing:
                        db.session.delete(existing)

        db.session.commit()
        return redirect(url_for("schedule.schedule_page", year=selected_year, month=selected_month, team_id=selected_team_id))

    return render_template("schedule.html",
        years=years,
        months=months,
        events=events,
        teams=teams,
        selected_year=selected_year,
        selected_month=selected_month,
        selected_team_id=selected_team_id,
        event_cards=event_cards
                          )