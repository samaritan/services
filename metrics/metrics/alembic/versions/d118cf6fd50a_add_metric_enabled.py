"""Add metric.enabled

Revision ID: d118cf6fd50a
Revises: df2e53ad7715
Create Date: 2021-02-01 13:26:34.888631

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "d118cf6fd50a"
down_revision = "df2e53ad7715"
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column(
        "metric",
        sa.Column("enabled", sa.Boolean(), server_default="0", nullable=True),
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column("metric", "enabled")
    # ### end Alembic commands ###
