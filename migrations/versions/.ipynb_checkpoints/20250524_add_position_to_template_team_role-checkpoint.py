"""Add position column to TemplateTeamRole"""

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '20250524_add_position_to_template_team_role'
down_revision = '5d22552a4655'
branch_labels = None
depends_on = None

def upgrade():
    op.add_column('template_team_role', sa.Column('position', sa.Integer(), nullable=True))

def downgrade():
    op.drop_column('template_team_role', 'position')
