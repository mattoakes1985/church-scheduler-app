from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_mail import Mail

login_manager = LoginManager()


db = SQLAlchemy()
mail = Mail()

@login_manager.user_loader
def load_user(user_id):
    return Volunteer.query.get(int(user_id))