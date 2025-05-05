from flask_wtf import FlaskForm
from wtforms import StringField
from wtforms.validators import DataRequired, Email
from flask_admin.form import Select2Widget
from wtforms_sqlalchemy.fields import QuerySelectMultipleField
from .core.models import Team

class VolunteerForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    email = StringField('Email', validators=[Email()])
    phone = StringField('Phone')
    teams = QuerySelectMultipleField('Teams', query_factory=lambda: Team.query.all(), widget=Select2Widget())
