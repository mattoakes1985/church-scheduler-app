from flask_admin.contrib.sqla import ModelView
from .forms import VolunteerForm
from app.core.models import Volunteer, Team, Role, TeamRole, VolunteerTeamRole, Event, EventTemplate, EventTeamRequirement

from wtforms_sqlalchemy.fields import QuerySelectField, QuerySelectMultipleField
from wtforms import SelectField
from wtforms.validators import DataRequired

from app.extensions import db
from flask_admin.form import Select2Widget
from flask import current_app

class VolunteerAdminView(ModelView):
    form = VolunteerForm

    def scaffold_form(self):
        form_class = super().scaffold_form()
        from wtforms import BooleanField
        form_class.is_lead = BooleanField('Is Lead')
        
        form_class.teams = QuerySelectMultipleField(
            'Teams',
            query_factory=lambda: db.session.query(Team).all(),
            widget=Select2Widget()
        )
        
        return form_class

def get_volunteers():
    return db.session.query(Volunteer).all()

def get_teams():
    return db.session.query(Team).all()

def get_roles():
    return db.session.query(Role).all()

class VolunteerTeamRoleAdmin(ModelView):
    form_columns = ['volunteer', 'team', 'role', 'is_lead']
    column_list = ['volunteer', 'team', 'role', 'is_lead']

    def scaffold_form(self):
        form_class = super().scaffold_form()
        form_class.volunteer = QuerySelectField(
            'Volunteer',
            query_factory=get_volunteers,
            widget=Select2Widget(),
            allow_blank=True
        )
        form_class.team = QuerySelectField(
            'Team',
            query_factory=get_teams,
            widget=Select2Widget(),
            allow_blank=True
        )
        form_class.role = QuerySelectField(
            'Role',
            query_factory=get_roles,
            widget=Select2Widget(),
            allow_blank=True
        )
        from wtforms import BooleanField
        form_class.is_lead = BooleanField('Is Lead')

        
        return form_class

class TeamRoleAdmin(ModelView):
    form_columns = ['team', 'role']
    column_list = ['team', 'role']

    def scaffold_form(self):
        form_class = super().scaffold_form()
        form_class.team = QuerySelectField(
            'Team',
            query_factory=get_teams,
            widget=Select2Widget(),
            allow_blank=True
        )
        form_class.role = QuerySelectField(
            'Role',
            query_factory=get_roles,
            widget=Select2Widget(),
            allow_blank=True
        )
        return form_class


class EventTeamRequirementAdmin(ModelView):
    form_columns = ['event', 'team', 'role']

    def scaffold_form(self):
        form_class = super().scaffold_form()

        form_class.event = QuerySelectField(
            'Event',
            query_factory=lambda: db.session.query(Event).all(),
            get_label='name',
            widget=Select2Widget(),
            allow_blank=True
        )

        form_class.team = QuerySelectField(
            'Team',
            query_factory=lambda: db.session.query(Team).all(),
            get_label='name',
            widget=Select2Widget(),
            allow_blank=True
        )

        form_class.role = QuerySelectField(
            'Role',
            query_factory=lambda: db.session.query(Role).all(),
            get_label='name',
            widget=Select2Widget(),
            allow_blank=True
        )

        return form_class

class EventAdminView(ModelView):
    form_columns = ['name', 'date', 'description', 'event_type', 'template_id']

    def scaffold_form(self):
        form_class = super().scaffold_form()

        # Override the event_type field completely
        class EventTypeSelectField(SelectField):
            def iter_choices(self):
                for value, label in self.choices:
                    yield (value, label, self.data == value)

        form_class.event_type = EventTypeSelectField(
            'Event Type',
            choices=[('service', 'Service'), ('special', 'Special Event')],
            validators=[DataRequired()]
        )

        # Handle the template field as a QuerySelectField
        form_class.template_id = QuerySelectField(
            'Template',
            query_factory=lambda: db.session.query(EventTemplate).all(),
            get_label='name',
            allow_blank=True
        )

        return form_class

    def scaffold_form(self):
        form_class = super().scaffold_form()
        form_class.template = QuerySelectField(
            'Template',
            query_factory=lambda: db.session.query(EventTemplate).all(),
            get_label='name',
            allow_blank=True
        )
        return form_class

class EventTemplateAdmin(ModelView):
    form_columns = ['name', 'description']  # Already done

    def scaffold_form(self):
        form_class = super().scaffold_form()
        # Explicitly remove any problematic fields
        if hasattr(form_class, 'events'):
            delattr(form_class, 'events')
        return form_class


class BasicModelView(ModelView):
    pass


