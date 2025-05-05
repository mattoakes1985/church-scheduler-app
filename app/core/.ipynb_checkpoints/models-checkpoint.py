from flask_sqlalchemy import SQLAlchemy
db = SQLAlchemy()



volunteer_team = db.Table('volunteer_team',
    db.Column('volunteer_id', db.Integer, db.ForeignKey('volunteer.id')),
    db.Column('team_id', db.Integer, db.ForeignKey('team.id'))
)

class Volunteer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True)
    phone = db.Column(db.String(20))

    teams = db.relationship('Team', secondary=volunteer_team, back_populates='volunteers')

    def __str__(self):
        return self.name

class Team(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)

    volunteers = db.relationship('Volunteer', secondary=volunteer_team, back_populates='teams')

    def __str__(self):
        return self.name

class Role(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    is_lead = db.Column(db.Boolean, default=False)

    def __str__(self):
        return self.name

class TeamRole(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    team_id = db.Column(db.Integer, db.ForeignKey('team.id'))
    role_id = db.Column(db.Integer, db.ForeignKey('role.id'))

    team = db.relationship('Team', backref=db.backref('team_roles', cascade="all, delete-orphan"))
    role = db.relationship('Role')

class VolunteerTeamRole(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    volunteer_id = db.Column(db.Integer, db.ForeignKey('volunteer.id'))
    team_id = db.Column(db.Integer, db.ForeignKey('team.id'))
    role_id = db.Column(db.Integer, db.ForeignKey('role.id'))

    volunteer = db.relationship('Volunteer', backref=db.backref('volunteer_roles', cascade="all, delete-orphan"))
    team = db.relationship('Team')
    role = db.relationship('Role')