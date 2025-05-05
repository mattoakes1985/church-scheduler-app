from flask_wtf import FlaskForm
from wtforms import StringField
from wtforms.validators import DataRequired, Email
from flask_admin.form import Select2Widget
from wtforms_sqlalchemy.fields import QuerySelectMultipleField

class VolunteerForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    email = StringField('Email', validators=[Email()])
    phone = StringField('Phone')

    @staticmethod
    def get_teams():
        from .core.models import Team
        return Team.query.all()

    teams = QuerySelectMultipleField('Teams', query_factory=get_teams.__func__, widget=Select2Widget())
