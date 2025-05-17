from app.extensions import login_manager
login_manager.init_app(app)
login_manager.login_view = 'auth.login'

# register authentication routes
from app.views.auth import auth_bp
app.register_blueprint(auth_bp)
