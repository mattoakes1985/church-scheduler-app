"""Fix volunteer_assignment.id auto increment

Revision ID: 5d22552a4655
Revises: 5c0ecb506e50
Create Date: 2025-05-24 17:33:44.167546
"""

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '5d22552a4655'
down_revision = 'b816b17f6232'  # or whatever your last valid revision is
branch_labels = None
depends_on = None

def upgrade():
    op.execute("CREATE SEQUENCE IF NOT EXISTS volunteer_assignment_id_seq")
    op.execute("ALTER TABLE volunteer_assignment ALTER COLUMN id SET DEFAULT nextval('volunteer_assignment_id_seq')")
    op.execute("SELECT setval('volunteer_assignment_id_seq', (SELECT MAX(id) FROM volunteer_assignment))")

def downgrade():
    op.execute("ALTER TABLE volunteer_assignment ALTER COLUMN id DROP DEFAULT")
    op.execute("DROP SEQUENCE IF EXISTS volunteer_assignment_id_seq")
