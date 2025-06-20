from flask import Blueprint, render_template, request, redirect, url_for, jsonify
from flask_login import login_required, current_user
from datetime import datetime, timedelta
from sqlalchemy.orm import aliased
from app.extensions import db
from app.core.models import (
    Event, VolunteerAssignment, VolunteerTeamRole,
    EventSong, Song, TemplateTeamRole, Role
)

worship_planning_bp = Blueprint("worship_planning", __name__, url_prefix="/worship-lead")

@worship_planning_bp.route("/")
@login_required
def planning():
    today = datetime.now()
    range_end = today + timedelta(weeks=6)
    events = Event.query.filter(Event.date >= today, Event.date <= range_end).order_by(Event.date).all()

    # Find editable events
    lead_assignments = db.session.query(VolunteerAssignment)\
        .join(VolunteerTeamRole,
              (VolunteerAssignment.volunteer_id == VolunteerTeamRole.volunteer_id) &
              (VolunteerAssignment.team_id == VolunteerTeamRole.team_id) &
              (VolunteerAssignment.role_id == VolunteerTeamRole.role_id))\
        .filter(
            VolunteerAssignment.volunteer_id == current_user.id,
            VolunteerTeamRole.is_lead == True
        ).all()

    editable_event_ids = {a.event_id for a in lead_assignments}
    editable, reference = [], []

    for event in events:
        TemplateTeamRoleAlias = aliased(TemplateTeamRole)
    
        assignments = db.session.query(VolunteerAssignment)\
            .join(Role, VolunteerAssignment.role_id == Role.id)\
            .join(Event, VolunteerAssignment.event_id == Event.id)\
            .outerjoin(
                TemplateTeamRoleAlias,
                db.and_(
                    TemplateTeamRoleAlias.team_id == VolunteerAssignment.team_id,
                    TemplateTeamRoleAlias.role_id == VolunteerAssignment.role_id,
                    TemplateTeamRoleAlias.template_id == Event.template_id
                )
            )\
            .filter(VolunteerAssignment.event_id == event.id)\
            .order_by(TemplateTeamRoleAlias.position.nullslast(), Role.name)\
            .all()
    
        band = [(a.role.name, a.volunteer.name) for a in assignments]
        songs = EventSong.query.filter_by(event_id=event.id).order_by(EventSong.position).all()
        event_data = {"event": event, "band": band, "songs": songs}
    
        if event.id in editable_event_ids:
            editable.append(event_data)
        else:
            reference.append(event_data)


    songs = Song.query.order_by(Song.name).all()
    return render_template("worship/planning.html", editable_events=editable, reference_events=reference, songs=songs)

@worship_planning_bp.route("/add-song", methods=["POST"])
@login_required
def add_song():
    event_id = request.form.get("event_id", type=int)
    song_id = request.form.get("song_id", type=int)
    custom_key = request.form.get("custom_key")
    notes = request.form.get("notes")

    if event_id and song_id:
        count = EventSong.query.filter_by(event_id=event_id).count()
        new_song = EventSong(
            event_id=event_id,
            song_id=song_id,
            custom_key=custom_key,
            notes=notes,
            position=count
        )
        db.session.add(new_song)
        db.session.commit()

    return redirect(url_for("worship_planning.planning"))

@worship_planning_bp.route("/remove-song/<int:event_song_id>")
@login_required
def remove_song(event_song_id):
    song = EventSong.query.get_or_404(event_song_id)
    db.session.delete(song)
    db.session.commit()
    return redirect(url_for("worship_planning.planning"))

@worship_planning_bp.route("/update-song", methods=["POST"])
@login_required
def update_song():
    event_song_id = request.form.get("event_song_id", type=int)
    custom_key = request.form.get("custom_key")
    notes = request.form.get("notes")

    song = EventSong.query.get_or_404(event_song_id)
    if custom_key is not None:
        song.custom_key = custom_key
    if notes is not None:
        song.notes = notes
    db.session.commit()
    return redirect(url_for("worship_planning.planning"))



@worship_planning_bp.route("/reorder-songs", methods=["POST"])
@login_required
def reorder_songs():
    data = request.get_json()
    for item in data["order"]:
        song = EventSong.query.get(int(item["id"]))
        if song:
            song.position = item["position"]
    db.session.commit()
    return jsonify({"status": "success"})