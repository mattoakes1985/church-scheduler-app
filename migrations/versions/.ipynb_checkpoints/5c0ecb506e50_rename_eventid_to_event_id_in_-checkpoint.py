"""Rename eventid to event_id in EventTeamRequirement"""

from alembic import op


# revision identifiers, used by Alembic.
revision = '5c0ecb506e50'
down_revision = 'b816b17f6232'
branch_labels = None
depends_on = None


def upgrade():
    # Rename the column in PostgreSQL
    op.alter_column('event_team_requirement', 'eventid', new_column_name='event_id')


def downgrade():
    op.alter_column('event_team_requirement', 'event_id', new_column_name='eventid')
