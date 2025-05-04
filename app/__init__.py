from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
from flask_admin.form import Select2Widget
from flask_wtf import FlaskForm
from wtforms_sqlalchemy.fields import QuerySelectMultipleField



db = SQLAlchemy()

def create_app():
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///church.db'
    app.config['SECRET_KEY'] = 'your-secret-key'

    db.init_app(app)

    # Define custom form and admin
    from .core.models import Volunteer, Team

    def team_choices():
        return Team.query.all()

    from wtforms import StringField
    from wtforms.validators import DataRequired, Email

    class VolunteerForm(FlaskForm):
        name = StringField('Name', validators=[DataRequired()])
        email = StringField('Email', validators=[Email()])
        phone = StringField('Phone')
        teams = QuerySelectMultipleField('Teams', query_factory=team_choices, widget=Select2Widget())

    class VolunteerAdmin(ModelView):
        form = VolunteerForm
        form_columns = ['name', 'email', 'phone', 'teams']

    # Set up admin
    admin = Admin(app, name="Church Scheduler Admin", template_mode='bootstrap4')
    admin.add_view(VolunteerAdmin(Volunteer, db.session))
    admin.add_view(ModelView(Team, db.session))

    with app.app_context():
        from . import routes
        from .core import models
        db.create_all()

    return app
