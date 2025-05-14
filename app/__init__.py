from flask import Flask
from flask_admin import Admin
from flask_migrate import Migrate

from .admin import VolunteerAdminView, VolunteerTeamRoleAdmin, TeamRoleAdmin, BasicModelView, EventTeamRequirementAdmin, EventAdminView, EventTemplateAdmin, TemplateTeamRoleAdmin, AdminHomeView 

from .forms import VolunteerForm

from app.core.models import Volunteer, Team, Role, TeamRole, VolunteerTeamRole, Event, EventTemplate, EventTeamRequirement, TemplateTeamRole

from app.extensions import db
from app.core.models import Event, Team, Role

from .extensions import db, login_manager



def create_app():
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///church.db'
    app.config['SECRET_KEY'] = 'your-secret-key'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    db.init_app(app)
    Migrate(app, db)  # ✅ Register migration support
    login_manager.init_app(app)  # ✅ Properly attaches it
   
    from app.core.models import Volunteer
    @login_manager.user_loader
    def load_user(user_id):
        return Volunteer.query.get(int(user_id))
    login_manager.login_view = 'main.login'  # Optional, if you have a login route


    with app.app_context():
        from . import routes
        from .core import models
        from .dashboard import DashboardView


    # Set up admin
    admin = Admin(
        app,
        name="Church Scheduler Admin",
        #index_view=AdminHomeView(),
        template_mode='bootstrap4'
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
    admin.add_view(EventAdminView(Event, db.session, category='Events'))
    admin.add_view(EventTeamRequirementAdmin(EventTeamRequirement, db.session, category='Events'))
    admin.add_view(EventTemplateAdmin(EventTemplate, db.session, category='Events'))
    admin.add_view(TemplateTeamRoleAdmin(TemplateTeamRole, db.session, category='Events'))


    from app.views.schedule import schedule_bp
    app.register_blueprint(schedule_bp)
    
    from app.views.schedule_dashboard import schedule_dashboard_bp
    app.register_blueprint(schedule_dashboard_bp)


    
    from .routes import main
    app.register_blueprint(main)


    return app