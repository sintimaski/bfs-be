"""project vol added to car_product

Revision ID: 4c9d5664a944
Revises: eb4264685aa0
Create Date: 2020-12-08 11:37:07.183739

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '4c9d5664a944'
down_revision = 'eb4264685aa0'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('car_product', sa.Column('project', sa.Text(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('car_product', 'project')
    # ### end Alembic commands ###
