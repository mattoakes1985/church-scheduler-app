"""Fix autoincrement on volunteer_availability.id

Revision ID: a01b67a3cb41
Revises: 20250524_add_position_to_template_team_role
Create Date: 2025-05-24 23:30:41.321545
"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'a01b67a3cb41'
down_revision = '20250524_add_position_to_template_team_role'
branch_labels = None
depends_on = None


def upgrade():
    # Create sequence explicitly
    op.execute("CREATE SEQUENCE IF NOT EXISTS volunteer_availability_id_seq")

    # Attach sequence to column
    op.execute("""
        ALTER TABLE volunteer_availability
        ALTER COLUMN id SET DEFAULT nextval('volunteer_availability_id_seq'),
        ALTER COLUMN id SET NOT NULL
    """)

    # Ensure sequence is set to correct next value
    op.execute("""
        SELECT setval('volunteer_availability_id_seq', COALESCE((SELECT MAX(id) FROM volunteer_availability), 1) + 1, false)
    """)


def downgrade():
    # Remove the default and drop the sequence
    op.execute("ALTER TABLE volunteer_availability ALTER COLUMN id DROP DEFAULT")
    op.execute("DROP SEQUENCE IF EXISTS volunteer_availability_id_seq")
