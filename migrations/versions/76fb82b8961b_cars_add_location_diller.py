"""common add location diller

Revision ID: 76fb82b8961b
Revises: 920ac7659cb4
Create Date: 2020-09-15 08:23:44.523023

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "76fb82b8961b"
down_revision = "920ac7659cb4"
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column(
        "car_product", sa.Column("location_diller", sa.Text(), nullable=True)
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column("car_product", "location_diller")
    # ### end Alembic commands ###
