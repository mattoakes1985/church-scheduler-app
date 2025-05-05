from flask_admin.contrib.sqla import ModelView
from .forms import VolunteerForm
from .core.models import Team
from wtforms_sqlalchemy.fields import QuerySelectMultipleField
from flask_admin.form import Select2Widget

class VolunteerAdminView(ModelView):
    form = VolunteerForm

    def scaffold_form(self):
        form_class = super().scaffold_form()
        form_class.teams = QuerySelectMultipleField(
            'Teams',
            query_factory=lambda: self.session.query(Team).all(),
            widget=Select2Widget()
        )
        return form_class

        # No form_columns — allow automatic inference


class BasicModelView(ModelView):
    pass

