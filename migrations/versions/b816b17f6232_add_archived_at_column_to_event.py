"""Add archived_at column to Event"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'b816b17f6232'
down_revision = 'c8c71ef4fe24'
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table('event', schema=None) as batch_op:
        batch_op.add_column(sa.Column('archived_at', sa.DateTime(), nullable=True))


def downgrade():
    with op.batch_alter_table('event', schema=None) as batch_op:
        batch_op.drop_column('archived_at')
