from flask import Flask
from flask_admin import Admin

from .admin import VolunteerAdminView, VolunteerTeamRoleAdmin, TeamRoleAdmin, BasicModelView

from .forms import VolunteerForm
from .core.models import Volunteer, Team, Role, TeamRole, VolunteerTeamRole

from app.extensions import db


def create_app():
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///church.db'
    app.config['SECRET_KEY'] = 'your-secret-key'

    db.init_app(app)

    with app.app_context():
        from . import routes
        from .core import models
        

        
        db.create_all()

    # Set up admin
    admin = Admin(
        app,
        name="Church Scheduler Admin",
        template_mode='bootstrap4',
        base_template='admin/my_base.html'
    )
    
    admin.add_view(VolunteerAdminView(Volunteer, db.session, endpoint='volunteers'))
    admin.add_view(BasicModelView(Team, db.session, endpoint='teams'))
    admin.add_view(BasicModelView(Role, db.session, endpoint='roles'))
    admin.add_view(TeamRoleAdmin(TeamRole, db.session, endpoint='teamroles'))
    admin.add_view(VolunteerTeamRoleAdmin(VolunteerTeamRole, db.session, endpoint='volunteerteamroles'))


    return app