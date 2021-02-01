"""Add project_metric server default to enabled

Revision ID: df2e53ad7715
Revises: 1e91879e2aa5
Create Date: 2021-02-01 13:15:40.404800

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "df2e53ad7715"
down_revision = "1e91879e2aa5"
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('project_metric', 'enabled', server_default='0')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('project_metric', 'enabled', server_default=None)
    # ### end Alembic commands ###
