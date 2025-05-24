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
    op.execute("""
        DO $$
        BEGIN
            IF NOT EXISTS (
                SELECT 1 FROM pg_class WHERE relname = 'volunteer_availability_id_seq'
            ) THEN
                CREATE SEQUENCE volunteer_availability_id_seq;
            END IF;
        END
        $$;
    """)
    op.execute("""
        ALTER TABLE volunteer_availability
        ALTER COLUMN id SET DEFAULT nextval('volunteer_availability_id_seq');
    """)
    op.execute("""
        ALTER SEQUENCE volunteer_availability_id_seq
        OWNED BY volunteer_availability.id;
    """)



def downgrade():
    # Remove the default and drop the sequence
    op.execute("ALTER TABLE volunteer_availability ALTER COLUMN id DROP DEFAULT")
    op.execute("DROP SEQUENCE IF EXISTS volunteer_availability_id_seq")
