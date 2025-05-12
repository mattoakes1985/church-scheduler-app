from flask_admin.contrib.sqla import ModelView
from .forms import VolunteerForm
from app.core.models import Volunteer, Team, Role, TeamRole, VolunteerTeamRole, Event, EventTemplate, EventTeamRequirement, TemplateTeamRole

from wtforms_sqlalchemy.fields import QuerySelectField, QuerySelectMultipleField 
from wtforms import SelectField
from wtforms.validators import DataRequired

from app.extensions import db

from flask_admin.form import Select2Widget
from flask_admin.contrib.sqla.filters import FilterEqual
from flask_admin.contrib.sqla.filters import BaseSQLAFilter

from flask import current_app
from flask import request

from sqlalchemy import extract



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


#Volunteer Team Role Section:

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


#Team Role Admin Section
        
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



#Event Name Filter Section

class EventNameFilter(BaseSQLAFilter):
    def apply(self, query, value, alias=None):
        return query.filter(EventTeamRequirement.event_id == value)

    def operation(self):
        return 'equals'

    def get_options(self, view):
        from flask import has_app_context
    
        if not has_app_context():
            return []
    
        return [
            (e.id, f"{e.name} ({e.date.strftime('%Y-%m-%d')})")
            for e in db.session.query(Event).order_by(Event.date.desc()).all()
        ]




from flask_admin.contrib.sqla.filters import FilterEqual


#Event Team Requirement Section

class EventTeamRequirementAdmin(ModelView):
    form_columns = ['event', 'team', 'role']
    column_list = ['event', 'team', 'role']
    list_template = 'admin/event_team_filtered.html'
    can_view_details = True
    

    def scaffold_form(self):
        form_class = super().scaffold_form()

        form_class.event = QuerySelectField(
            'Event',
            query_factory=lambda: db.session.query(Event).order_by(Event.date.desc()).all(),
            get_label=lambda e: f"{e.name} ({e.date.strftime('%Y-%m-%d')})",
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

    def get_query(self):
        event_id = request.args.get('event_id', type=int)
        print(f"🧪 get_query: event_id={event_id}")
        query = super().get_query()
        if event_id:
            count = query.filter(EventTeamRequirement.event_id == event_id).count()
            print(f"🧪 Matching records: {count}")
            return query.filter(EventTeamRequirement.event_id == event_id)
        print("🧪 No event_id selected → suppressing all rows")
        return query.filter(False)

    
    def get_count_query(self):
        event_id = request.args.get('event_id', type=int)
        query = super().get_count_query()
        if event_id:
            return query.filter(EventTeamRequirement.event_id == event_id)
        return query.filter(False)


    def get_list(self, *args, **kwargs):
        context = self._build_filter_context()
        self._template_args.update(context)
        return super().get_list(*args, **kwargs)

    def _build_filter_context(self):
        years = db.session.query(extract('year', Event.date))\
            .distinct()\
            .order_by(extract('year', Event.date).desc()).all()
        selected_year = request.args.get('year', type=int)
        selected_event_id = request.args.get('event_id', type=int)
        events = []
        if selected_year:
            events = db.session.query(Event)\
                .filter(extract('year', Event.date) == selected_year)\
                .order_by(Event.date.desc()).all()
        return {
            'years': [y[0] for y in years],
            'selected_year': selected_year,
            'events': events,
            'selected_event_id': selected_event_id
        }

    def render(self, template, **kwargs):
        # all your filter prep
        years = db.session.query(extract('year', Event.date))\
            .distinct()\
            .order_by(extract('year', Event.date).desc()).all()
        selected_year = request.args.get('year', type=int)
        selected_event_id = request.args.get('event_id', type=int)
    
        events = []
        if selected_year:
            events = db.session.query(Event)\
                .filter(extract('year', Event.date) == selected_year)\
                .order_by(Event.date.desc()).all()
    
        # Preload filtered rows
        rows = []
        if selected_event_id:
            rows = db.session.query(EventTeamRequirement)\
                .filter_by(event_id=selected_event_id)\
                .all()
    
        kwargs.update({
            'years': [y[0] for y in years],
            'selected_year': selected_year,
            'events': events,
            'selected_event_id': selected_event_id,
            'records': rows
        })
    
        return super().render(template, **kwargs)



        

class EventAdminView(ModelView):
    form_columns = ['name', 'date', 'description', 'event_type', 'template']

    form_overrides = {
        'event_type': SelectField
    }

    form_args = {
        'event_type': {
            'label': 'Event Type',
            'choices': [('service', 'Service'), ('special', 'Special Event')],
            'validators': [DataRequired()],
            'coerce': str
        }
    }

    form_extra_fields = {
        'template': QuerySelectField(
            'Template',
            query_factory=lambda: db.session.query(EventTemplate).all(),
            get_label='name',
            allow_blank=True
        )
    }
    
    def after_model_change(self, form, model, is_created):
        from flask import current_app
    
        if is_created and model.template_id:
            template_roles = db.session.query(TemplateTeamRole).filter_by(template_id=model.template_id).all()
            current_app.logger.info(f"🧩 Found {len(template_roles)} TemplateTeamRoles for template {model.template_id}")

            for tr in template_roles:
                current_app.logger.info(f"→ Adding {tr.team.name} - {tr.role.name}")
                req = EventTeamRequirement(
                    event_id=model.id,
                    team_id=tr.team_id,
                    role_id=tr.role_id
                )
                db.session.add(req)

        db.session.commit()
        current_app.logger.info("✅ Committed EventTeamRequirement records")

    
    def after_model_save(self, form, model, is_created):
        from flask import current_app
        current_app.logger.info("🚨 after_model_save triggered")
        
        if model.template_id and not model.team_requirements:
            template_roles = db.session.query(TemplateTeamRole).filter_by(template_id=model.template_id).all()
            current_app.logger.info(f"Found {len(template_roles)} template roles for template {model.template_id}")
    
            for tr in template_roles:
                current_app.logger.info(f"Adding team: {tr.team.name}, role: {tr.role.name}")
                req = EventTeamRequirement(
                    event_id=model.id,
                    team_id=tr.team_id,
                    role_id=tr.role_id
                )
                db.session.add(req)
    
            db.session.commit()
            current_app.logger.info(f"Committed {len(template_roles)} EventTeamRequirements for event {model.name}")



class EventTemplateAdmin(ModelView):
    form_columns = ['name', 'description']  # Already done

    def scaffold_form(self):
        form_class = super().scaffold_form()
        # Explicitly remove any problematic fields
        if hasattr(form_class, 'events'):
            delattr(form_class, 'events')
        return form_class



class TemplateTeamRoleAdmin(ModelView):
    form_columns = ['template', 'team', 'role']

    def scaffold_form(self):
        form_class = super().scaffold_form()

        form_class.template = QuerySelectField(
            'Template',
            query_factory=lambda: db.session.query(EventTemplate).all(),
            get_label='name',
            allow_blank=True
        )

        form_class.team = QuerySelectField(
            'Team',
            query_factory=lambda: db.session.query(Team).all(),
            get_label='name',
            allow_blank=True
        )

        form_class.role = QuerySelectField(
            'Role',
            query_factory=lambda: db.session.query(Role).all(),
            get_label='name',
            allow_blank=True
        )

        return form_class


class BasicModelView(ModelView):
    pass
