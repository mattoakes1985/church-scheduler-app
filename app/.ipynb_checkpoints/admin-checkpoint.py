from flask_admin.contrib.sqla import ModelView
from .forms import VolunteerForm
from app.core.models import Team, Volunteer, Role, TeamRole, VolunteerTeamRole
from wtforms_sqlalchemy.fields import QuerySelectField, QuerySelectMultipleField
from app.extensions import db
from flask_admin.form import Select2Widget
from flask import current_app

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

class BasicModelView(ModelView):
    pass

from flask_admin import BaseView, expose
import plotly.graph_objs as go
import json
import plotly

class DashboardView(BaseView):
    @expose('/')
    def index(self):
        # Fetch links: who has what role in what team
        connections = db.session.query(
            Volunteer.name,
            Team.name,
            Role.name
        )\
            .join(VolunteerTeamRole, Volunteer.id == VolunteerTeamRole.volunteer_id)\
            .join(Team, Team.id == VolunteerTeamRole.team_id)\
            .join(Role, Role.id == VolunteerTeamRole.role_id).all()

        nodes = set()
        edges = []

        for volunteer, team, role in connections:
            nodes.update([volunteer, team, role])
            edges.append((volunteer, team))
            edges.append((volunteer, role))
            edges.append((team, role))

        node_list = list(nodes)
        node_idx = {name: i for i, name in enumerate(node_list)}

        edge_trace = go.Scatter(
            x=[], y=[], line=dict(width=0.5, color='#888'), hoverinfo='none', mode='lines')
        node_trace = go.Scatter(
            x=[], y=[], text=[], mode='markers+text', textposition='top center',
            marker=dict(showscale=False, color=[], size=10, line_width=2))

        import networkx as nx
        G = nx.Graph()
        G.add_edges_from([(node_idx[src], node_idx[tgt]) for src, tgt in edges])
        pos = nx.spring_layout(G, seed=42)

        for idx, name in enumerate(node_list):
            x, y = pos[idx]
            node_trace['x'] += (x,)
            node_trace['y'] += (y,)
            node_trace['text'] += (name,)
            node_trace['marker']['color'] += ('#1f77b4',)

        for edge in edges:
            x0, y0 = pos[node_idx[edge[0]]]
            x1, y1 = pos[node_idx[edge[1]]]
            edge_trace['x'] += (x0, x1, None)
            edge_trace['y'] += (y0, y1, None)

        fig = go.Figure(data=[edge_trace, node_trace],
                        layout=go.Layout(
                            title=dict(text='Team & Role Network', font=dict(size=16)),
                            showlegend=False,
                            hovermode='closest',
                            margin=dict(b=20, l=5, r=5, t=40),
                            xaxis=dict(visible=False),
                            yaxis=dict(visible=False)))

        graph_json = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)

        return self.render('admin/dashboard.html', graphJSON=graph_json)
