"""cars body_type

Revision ID: c317ffbb80bf
Revises: 0cb728ab197d
Create Date: 2020-10-19 08:08:27.316549

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'c317ffbb80bf'
down_revision = '0cb728ab197d'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('car_product', sa.Column('body_type', sa.Text(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('car_product', 'body_type')
    # ### end Alembic commands ###
