"""R2BUSINESS last_update needs_check added

Revision ID: 712849482245
Revises: 21de5dfe33b0
Create Date: 2021-03-31 04:46:21.213382

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '712849482245'
down_revision = '21de5dfe33b0'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('r2_g_business', sa.Column('last_update', postgresql.JSON(astext_type=sa.Text()), nullable=True))
    op.add_column('r2_g_business', sa.Column('needs_check', sa.Boolean(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('r2_g_business', 'needs_check')
    op.drop_column('r2_g_business', 'last_update')
    # ### end Alembic commands ###
