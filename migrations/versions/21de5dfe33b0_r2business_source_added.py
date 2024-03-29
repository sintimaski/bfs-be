"""R2BUSINESS source added

Revision ID: 21de5dfe33b0
Revises: aa4439dc4c1a
Create Date: 2021-03-17 10:02:23.713780

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '21de5dfe33b0'
down_revision = 'aa4439dc4c1a'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('r2_g_business', sa.Column('status', sa.Text(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('r2_g_business', 'status')
    # ### end Alembic commands ###
