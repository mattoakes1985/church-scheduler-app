from flask import Blueprint, render_template, request, redirect, url_for
from app.extensions import db
from sqlalchemy import extract, and_
from app.core.models import (
    Event, Team, Role, Volunteer, VolunteerAvailability,
    EventTeamRequirement, VolunteerTeamRole, VolunteerAssignment, TemplateTeamRole
)
from app.decorators import admin_required

schedule_bp = Blueprint('schedule', __name__, url_prefix='/schedule')

@schedule_bp.route("/", methods=["GET", "POST"])
@admin_required
def schedule_page():
    selected_year = request.values.get("year", type=int)
    selected_month = request.values.get("month", type=int)
    selected_team_id = request.values.get("team_id", type=int)

    # Years for dropdown
    raw_years = db.session.query(extract('year', Event.date)).distinct().order_by(extract('year', Event.date).desc()).all()
    years = [int(row[0]) for row in raw_years if row[0] is not None]

    months = []
    events = []
    teams = []
    event_cards = {}

    if selected_year:
        months_query = db.session.query(extract('month', Event.date))\
            .filter(extract('year', Event.date) == selected_year).distinct()
        month_nums = [int(m[0]) for m in months_query if m[0] is not None]
        months = [(m, [
            "January", "February", "March", "April", "May", "June",
            "July", "August", "September", "October", "November", "December"
        ][m - 1]) for m in month_nums]

    if selected_year and selected_month:
        events = Event.query.filter(
            and_(
                extract('year', Event.date) == selected_year,
                extract('month', Event.date) == selected_month,
                Event.archived_at.is_(None)
            )
        ).order_by(Event.date).all()

        event_ids = [e.id for e in events]

        if event_ids:
            teams = db.session.query(Team).join(EventTeamRequirement)\
                .filter(EventTeamRequirement.event_id.in_(event_ids))\
                .distinct().all()

        if selected_team_id:
            # Preload role position for template_id = 3
            position_lookup = {
                (ttr.team_id, ttr.role_id): ttr.position
                for ttr in db.session.query(TemplateTeamRole)
                .filter(TemplateTeamRole.template_id == 3)
            }

            for event in events:
                requirements = db.session.query(EventTeamRequirement).filter_by(
                    event_id=event.id,
                    team_id=selected_team_id
                ).all()

                # Sort using template position and then role name as fallback
                requirements.sort(
                    key=lambda r: (
                        position_lookup.get((r.team_id, r.role_id), 9999),
                        r.role.name if r.role else ""
                    )
                )

                available_ids = db.session.query(VolunteerAvailability.volunteer_id)\
                    .filter_by(event_id=event.id).subquery()

                eligible = {}
                assignments = {}

                for req in requirements:
                    eligible[req.role_id] = db.session.query(Volunteer)\
                        .join(VolunteerTeamRole)\
                        .join(VolunteerAvailability)\
                        .filter(
                            VolunteerAvailability.event_id == event.id,
                            VolunteerAvailability.status == 'yes',
                            VolunteerTeamRole.team_id == selected_team_id,
                            VolunteerTeamRole.role_id == req.role_id,
                            Volunteer.id == VolunteerAvailability.volunteer_id
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

@schedule_bp.route("/toggle-lock/<int:event_id>", methods=["POST"])
def toggle_event_lock(event_id):
    event = Event.query.get_or_404(event_id)
    event.availability_locked = not event.availability_locked
    db.session.commit()
    return redirect(request.referrer or url_for("schedule.schedule_page"))
