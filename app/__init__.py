from flask import Flask
from flask_admin import Admin
from flask_migrate import Migrate

from .admin import (
    VolunteerAdminView, VolunteerTeamRoleAdmin, TeamRoleAdmin, BasicModelView,
    EventTeamRequirementAdmin, EventAdminView, EventTemplateAdmin, TemplateTeamRoleAdmin,
    AdminHomeView
)

from .forms import VolunteerForm
from app.extensions import db, login_manager
from app.core.models import (
    Volunteer, Team, Role, TeamRole, VolunteerTeamRole,
    Event, EventTemplate, EventTeamRequirement, TemplateTeamRole, Song
)
from app.views.auth import auth_bp
from .dashboard import DashboardView

def create_app():
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///church.db'
    app.config['SECRET_KEY'] = 'your-secret-key'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db.init_app(app)
    Migrate(app, db)

    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'

    @login_manager.user_loader
    def load_user(user_id):
        return Volunteer.query.get(int(user_id))

    with app.app_context():
        from . import routes
        from .core import models

    # Admin setup
    admin = Admin(
        app,
        name="Church Scheduler Admin",
        template_mode='bootstrap4'
    )

    with app.app_context():
            from . import routes
            from .core import models
            from .dashboard import DashboardView
            from .admin import SongAdminView
    
    admin.add_view(DashboardView())
    admin.add_view(VolunteerAdminView(Volunteer, db.session, endpoint='volunteers', category='People & Teams'))
    admin.add_view(BasicModelView(Team, db.session, endpoint='teams', category='People & Teams'))
    admin.add_view(BasicModelView(Role, db.session, endpoint='roles', category='People & Teams'))
    admin.add_view(TeamRoleAdmin(TeamRole, db.session, endpoint='teamroles', category='People & Teams'))
    admin.add_view(VolunteerTeamRoleAdmin(VolunteerTeamRole, db.session, endpoint='volunteerteamroles', category='People & Teams'))

    admin.add_view(EventAdminView(Event, db.session, category='Events'))
    admin.add_view(EventTeamRequirementAdmin(EventTeamRequirement, db.session, category='Events'))
    admin.add_view(EventTemplateAdmin(EventTemplate, db.session, category='Events'))
    admin.add_view(TemplateTeamRoleAdmin(TemplateTeamRole, db.session, category='Events'))
    admin.add_view(SongAdminView(Song, db.session, category='Worship'))


    # Blueprints
    app.register_blueprint(auth_bp)
    from app.views.schedule import schedule_bp
    app.register_blueprint(schedule_bp)

    from app.views.schedule_dashboard import schedule_dashboard_bp
    app.register_blueprint(schedule_dashboard_bp)

    from app.views.availability import availability_bp
    app.register_blueprint(availability_bp)

    from app.views.volunteer.dashboard import volunteer_dashboard_bp
    from app.views.volunteer.schedule import volunteer_schedule_bp
    app.register_blueprint(volunteer_dashboard_bp)
    app.register_blueprint(volunteer_schedule_bp)

    from app.views.worship.planning import worship_planning_bp
    app.register_blueprint(worship_planning_bp)

    
    from .routes import main
    app.register_blueprint(main)

    @app.errorhandler(403)
    def forbidden(error):
        from flask import flash, redirect, url_for
        flash("You do not have permission to access that page.", "warning")
        return redirect(url_for('main.volunteer_portal'))


    return app
