from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_admin import Admin

from .admin import VolunteerAdminView, BasicModelView
from .forms import VolunteerForm
from .core.models import Volunteer, Team, Role, TeamRole, VolunteerTeamRole


db = SQLAlchemy()

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

    admin.add_view(VolunteerAdminView(Volunteer, db.session))
    admin.add_view(BasicModelView(Team, db.session))
    admin.add_view(BasicModelView(Role, db.session))
    admin.add_view(BasicModelView(TeamRole, db.session))
    admin.add_view(BasicModelView(VolunteerTeamRole, db.session))

    return app