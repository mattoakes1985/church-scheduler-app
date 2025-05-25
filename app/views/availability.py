from flask import Blueprint, render_template, request, redirect, url_for
from datetime import datetime, timedelta
from app.extensions import db
from app.core.models import (
    Volunteer, Event, Team, Role,
    VolunteerTeamRole, VolunteerAvailability
)
from flask_login import login_required, current_user




availability_bp = Blueprint('availability', __name__, url_prefix='/availability')

@availability_bp.route("/", methods=["GET", "POST"])
@login_required
def availability_page():
    from datetime import timedelta
    volunteer = current_user
    if not volunteer:
        return "No volunteer available in the database."

    today = datetime.today()
    in_2_months = today + timedelta(days=60)

    # Pagination
    page = request.args.get("page", 1, type=int)
    per_page = 8

    upcoming_events_query = Event.query.filter(
        Event.date >= today,
        Event.date <= in_2_months
    ).order_by(Event.date)

    pagination = upcoming_events_query.paginate(page=page, per_page=per_page, error_out=False)
    upcoming_events = pagination.items

    team_ids = [vtr.team_id for vtr in volunteer.volunteer_roles]
    teams = Team.query.filter(Team.id.in_(team_ids)).all()

    team_roles = {}
    for vtr in volunteer.volunteer_roles:
        team_roles.setdefault(vtr.team_id, []).append(vtr.role)

    if request.method == "POST":
        if "delete_event_id" in request.form:
            event_id = int(request.form["delete_event_id"])
            VolunteerAvailability.query.filter_by(
                volunteer_id=volunteer.id,
                event_id=event_id
            ).delete()
            db.session.commit()
            return redirect(url_for("availability.availability_page", page=page))

        for key in request.form:
            if key.startswith("availability_"):
                event_id = int(key.split("_")[1])
                status = request.form[key]
                team_id = request.form.get(f"team_{event_id}", type=int)

                event = Event.query.get(event_id)
                if not event or event.availability_locked:
                    continue  # skip locked events

                if status not in {"yes", "no", "maybe"}:
                    continue


                existing = VolunteerAvailability.query.filter_by(
                    volunteer_id=volunteer.id,
                    event_id=event_id
                ).first()
                
                if existing:
                    existing.status = status
                    
                else:
                    db.session.add(VolunteerAvailability(
                        volunteer_id=volunteer.id,
                        event_id=event.id,
                        status=status
                    ))


        db.session.commit()
        print("AFTER COMMIT:")
        for row in VolunteerAvailability.query.all():
            print(row.event_id, row.volunteer_id, row.status)

        return redirect(url_for("availability.availability_page", page=page))

    submitted = VolunteerAvailability.query.filter_by(volunteer_id=volunteer.id).all()
    print("Saved availability in DB:")
    for row in VolunteerAvailability.query.all():
        print(row.event_id, row.volunteer_id, row.status)

    
    availability_map = {
        s.event_id: {"status": s.status}
        for s in submitted
    }


    return render_template("volunteer/availability.html",
        volunteer=volunteer,
        events=upcoming_events,
        teams=teams,
        team_roles=team_roles,
        availability_map=availability_map,
        pagination=pagination
    )
