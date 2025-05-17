from app.extensions import db
from datetime import datetime
from flask_login import UserMixin 

# Association table for many-to-many Volunteer <-> Team
volunteer_team = db.Table('volunteer_team',
    db.Column('volunteer_id', db.Integer, db.ForeignKey('volunteer.id')),
    db.Column('team_id', db.Integer, db.ForeignKey('team.id'))
)

class Volunteer(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True)
    phone = db.Column(db.String(20))

    teams = db.relationship('Team', secondary=volunteer_team, back_populates='volunteers')
    volunteer_roles = db.relationship('VolunteerTeamRole', back_populates='volunteer')
    availabilities = db.relationship('VolunteerAvailability', back_populates='volunteer')



    def __str__(self):
        return self.name

class Team(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)

    volunteers = db.relationship('Volunteer', secondary=volunteer_team, back_populates='teams')
    team_roles = db.relationship('TeamRole', back_populates='team', cascade='all, delete-orphan')
    volunteer_team_roles = db.relationship('VolunteerTeamRole', back_populates='team', cascade='all, delete-orphan')

    def __str__(self):
        return self.name

class Role(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    is_lead = db.Column(db.Boolean, default=False)  # Hidden flag, not for UI

    team_roles = db.relationship('TeamRole', back_populates='role', cascade='all, delete-orphan')
    volunteer_team_roles = db.relationship('VolunteerTeamRole', back_populates='role', cascade='all, delete-orphan')

    def __str__(self):
        return self.name

class TeamRole(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    team_id = db.Column(db.Integer, db.ForeignKey('team.id'))
    role_id = db.Column(db.Integer, db.ForeignKey('role.id'))
    template_id = db.Column(db.Integer, db.ForeignKey('event_template.id'), nullable=True)
    template = db.relationship('EventTemplate', backref='team_roles')
    team = db.relationship('Team', back_populates='team_roles')
    role = db.relationship('Role', back_populates='team_roles')

class VolunteerTeamRole(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    volunteer_id = db.Column(db.Integer, db.ForeignKey('volunteer.id'))
    team_id = db.Column(db.Integer, db.ForeignKey('team.id'))
    role_id = db.Column(db.Integer, db.ForeignKey('role.id'))
    is_lead = db.Column(db.Boolean, default=False)

    volunteer = db.relationship('Volunteer', back_populates='volunteer_roles')
    team = db.relationship('Team', back_populates='volunteer_team_roles')
    role = db.relationship('Role', back_populates='volunteer_team_roles')

class Event(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    description = db.Column(db.Text, nullable=True)
    event_type = db.Column(db.String(50), nullable=False)

    availability_locked = db.Column(db.Boolean, default=False) 

    template_id = db.Column(db.Integer, db.ForeignKey('event_template.id'), nullable=True)
    template = db.relationship('EventTemplate', backref='events')

    def __str__(self):
        return f"{self.name} ({self.date.strftime('%Y-%m-%d')})"



class EventTemplate(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)

    def __str__(self):
        return self.name
        
class EventTeamRequirement(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    event_id = db.Column(db.Integer, db.ForeignKey('event.id'), nullable=False)
    team_id = db.Column(db.Integer, db.ForeignKey('team.id'), nullable=False)
    role_id = db.Column(db.Integer, db.ForeignKey('role.id'), nullable=False)

    event = db.relationship('Event', backref='team_requirements')  # ← Add this
    team = db.relationship('Team')
    role = db.relationship('Role')

class TemplateTeamRole(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    template_id = db.Column(db.Integer, db.ForeignKey('event_template.id'), nullable=False)
    team_id = db.Column(db.Integer, db.ForeignKey('team.id'), nullable=False)
    role_id = db.Column(db.Integer, db.ForeignKey('role.id'), nullable=False)

    template = db.relationship('EventTemplate', backref='template_team_roles')
    team = db.relationship('Team')
    role = db.relationship('Role')


class VolunteerAvailability(db.Model):
    __tablename__ = 'volunteer_availability'
    __table_args__ = (
        db.UniqueConstraint('volunteer_id', 'event_id', name='uix_volunteer_event'),
    )
    id = db.Column(db.Integer, primary_key=True)
    volunteer_id = db.Column(db.Integer, db.ForeignKey('volunteer.id'), nullable=False)
    event_id = db.Column(db.Integer, db.ForeignKey('event.id'), nullable=False)
    team_id = db.Column(db.Integer, db.ForeignKey('team.id'), nullable=False)
    status = db.Column(db.String(10), nullable=False)  # 'yes', 'no', 'maybe'

    volunteer = db.relationship('Volunteer', back_populates='availabilities')
    event = db.relationship('Event', backref='volunteer_availability')
    team = db.relationship('Team')



class VolunteerAssignment(db.Model):
    __tablename__ = 'volunteer_assignment'
    id = db.Column(db.Integer, primary_key=True)
    volunteer_id = db.Column(db.Integer, db.ForeignKey('volunteer.id'), nullable=False)
    event_id = db.Column(db.Integer, db.ForeignKey('event.id'), nullable=False)
    team_id = db.Column(db.Integer, db.ForeignKey('team.id'), nullable=False)
    role_id = db.Column(db.Integer, db.ForeignKey('role.id'), nullable=False)

    volunteer = db.relationship('Volunteer', backref='assignments')
    event = db.relationship('Event', backref='assignments')
    team = db.relationship('Team', backref='assignments')
    role = db.relationship('Role', backref='assignments')

