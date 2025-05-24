from flask import Blueprint, render_template, request
from flask_login import login_required
from sqlalchemy import extract
from sqlalchemy.orm import aliased  
from app.extensions import db
from app.core.models import Team, Event, Role, VolunteerAssignment, EventTeamRequirement, TemplateTeamRole

       

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
        Event.archived_at == None,
        extract("year", Event.date) == selected_year,
        extract("month", Event.date) == selected_month
    ).order_by(Event.date).all()

    event_ids = [e.id for e in events]

    roles = []
    assignment_matrix = {}
    if selected_team:
        TemplateTeamRoleAlias = aliased(TemplateTeamRole)
    
        # Fetch roles ordered by TemplateTeamRole.position (if template is used)
        roles_query = db.session.query(Role).join(EventTeamRequirement)\
            .join(Event, EventTeamRequirement.event_id == Event.id)\
            .outerjoin(
                TemplateTeamRoleAlias,
                db.and_(
                    TemplateTeamRoleAlias.team_id == EventTeamRequirement.team_id,
                    TemplateTeamRoleAlias.role_id == EventTeamRequirement.role_id,
                    TemplateTeamRoleAlias.template_id == Event.template_id
                )
            )\
            .filter(EventTeamRequirement.event_id.in_(event_ids))\
            .filter(EventTeamRequirement.team_id == selected_team_id)\
            .group_by(Role.id, Role.name, Role.is_lead, TemplateTeamRoleAlias.position)\
            .order_by(TemplateTeamRoleAlias.position.nullslast(), Role.name)

    
        roles = roles_query.all()
    
        assignments = VolunteerAssignment.query.filter(
            VolunteerAssignment.event_id.in_(event_ids),
            VolunteerAssignment.team_id == selected_team_id
        ).all()
    
        for a in assignments:
            assignment_matrix[(a.event_id, a.role_id)] = a.volunteer


    # Song map
    from app.core.models import EventSong  # Add to top if not already
    songs_by_event = {}
    if event_ids:
        for s in EventSong.query.filter(EventSong.event_id.in_(event_ids)).order_by(EventSong.position).all():
            songs_by_event.setdefault(s.event_id, []).append(s)

    
    return render_template("volunteer/schedule.html",
        teams=teams,
        selected_team=selected_team,
        events=events,
        roles=roles,
        assignment_matrix=assignment_matrix,
        songs_by_event=songs_by_event
    )

