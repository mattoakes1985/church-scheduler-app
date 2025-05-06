from flask import Flask
from flask_admin import Admin
from flask_migrate import Migrate

from .admin import VolunteerAdminView, VolunteerTeamRoleAdmin, TeamRoleAdmin, BasicModelView, EventTeamRequirementAdmin
from .forms import VolunteerForm
from app.core.models import Volunteer, Team, Role, TeamRole, VolunteerTeamRole, Event, EventTemplate, EventTeamRequirement
from app.extensions import db
from app.core.models import Event, Team, Role





def create_app():
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///church.db'
    app.config['SECRET_KEY'] = 'your-secret-key'

    db.init_app(app)
    Migrate(app, db)  # ✅ Register migration support

    with app.app_context():
        from . import routes
        from .core import models
        from .dashboard import DashboardView



    # Set up admin
    admin = Admin(
        app,
        name="Church Scheduler Admin",
        template_mode='bootstrap4',
        base_template='admin/my_base.html'
    )

    # Dashboard (custom)
    admin.add_view(DashboardView())
    
    # People & Teams
    admin.add_view(VolunteerAdminView(Volunteer, db.session, endpoint='volunteers', category='People & Teams'))
    admin.add_view(BasicModelView(Team, db.session, endpoint='teams', category='People & Teams'))
    admin.add_view(BasicModelView(Role, db.session, endpoint='roles', category='People & Teams'))
    admin.add_view(TeamRoleAdmin(TeamRole, db.session, endpoint='teamroles', category='People & Teams'))
    admin.add_view(VolunteerTeamRoleAdmin(VolunteerTeamRole, db.session, endpoint='volunteerteamroles', category='People & Teams'))
    
    # Events
    admin.add_view(BasicModelView(Event, db.session, category='Events'))
    admin.add_view(BasicModelView(EventTemplate, db.session, category='Events'))
    admin.add_view(EventTeamRequirementAdmin(EventTeamRequirement, db.session, category='Events'))
    



    return app