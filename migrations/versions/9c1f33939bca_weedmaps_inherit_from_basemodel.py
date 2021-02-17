"""weedmaps inherit from BaseModel

Revision ID: 9c1f33939bca
Revises: 335ad9825bf5
Create Date: 2020-10-09 13:57:08.142762

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "9c1f33939bca"
down_revision = "335ad9825bf5"
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column(
        "weedmaps_product",
        sa.Column("created_at", sa.DateTime(), nullable=True),
    )
    op.add_column(
        "weedmaps_product",
        sa.Column("updated_at", sa.DateTime(), nullable=True),
    )
    op.add_column(
        "weedmaps_shop", sa.Column("created_at", sa.DateTime(), nullable=True)
    )
    op.add_column(
        "weedmaps_shop", sa.Column("updated_at", sa.DateTime(), nullable=True)
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column("weedmaps_shop", "updated_at")
    op.drop_column("weedmaps_shop", "created_at")
    op.drop_column("weedmaps_product", "updated_at")
    op.drop_column("weedmaps_product", "created_at")
    # ### end Alembic commands ###
