from .. import db

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

    volunteers = db.relationship('Volunteer', secondary='volunteer_team', back_populates='teams')

    def __str__(self):
        return self.name  # <- This is what shows in dropdowns
