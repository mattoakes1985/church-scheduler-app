from flask_admin.contrib.sqla import ModelView
from .forms import VolunteerForm

class VolunteerAdminView(ModelView):
    form = VolunteerForm
    form_columns = ['name', 'email', 'phone', 'teams']

class BasicModelView(ModelView):
    pass
