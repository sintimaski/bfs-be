"""BUSINESS mapped_to_id

Revision ID: 3cc829bbdf55
Revises: ac478543285e
Create Date: 2021-02-07 08:43:22.070743

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '3cc829bbdf55'
down_revision = 'ac478543285e'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('business', sa.Column('mapped_to_id', sa.Integer(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('business', 'mapped_to_id')
    # ### end Alembic commands ###
