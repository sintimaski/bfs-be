"""BUSINESS project field added

Revision ID: 58e567ebb762
Revises: 4c9d5664a944
Create Date: 2021-01-25 12:50:22.242089

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '58e567ebb762'
down_revision = '4c9d5664a944'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('business', sa.Column('project', sa.Text(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('business', 'project')
    # ### end Alembic commands ###