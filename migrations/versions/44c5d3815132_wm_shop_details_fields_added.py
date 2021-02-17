"""WM_shop details fields added

Revision ID: 44c5d3815132
Revises: 1572a0239a78
Create Date: 2020-09-09 13:31:44.442430

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "44c5d3815132"
down_revision = "1572a0239a78"
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column(
        "weedmaps_shop", sa.Column("aboutus", sa.Text(), nullable=True)
    )
    op.add_column(
        "weedmaps_shop",
        sa.Column("amenities", postgresql.ARRAY(sa.Text()), nullable=True),
    )
    op.add_column(
        "weedmaps_shop", sa.Column("announcement", sa.Text(), nullable=True)
    )
    op.add_column(
        "weedmaps_shop",
        sa.Column(
            "business_hours",
            postgresql.JSON(astext_type=sa.Text()),
            nullable=True,
        ),
    )
    op.add_column("weedmaps_shop", sa.Column("email", sa.Text(), nullable=True))
    op.add_column(
        "weedmaps_shop", sa.Column("f_t_announcement", sa.Text(), nullable=True)
    )
    op.add_column("weedmaps_shop", sa.Column("intro", sa.Text(), nullable=True))
    op.add_column("weedmaps_shop", sa.Column("phone", sa.Text(), nullable=True))
    op.add_column(
        "weedmaps_shop", sa.Column("services", sa.Text(), nullable=True)
    )
    op.add_column(
        "weedmaps_shop", sa.Column("website", sa.Text(), nullable=True)
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column("weedmaps_shop", "website")
    op.drop_column("weedmaps_shop", "services")
    op.drop_column("weedmaps_shop", "phone")
    op.drop_column("weedmaps_shop", "intro")
    op.drop_column("weedmaps_shop", "f_t_announcement")
    op.drop_column("weedmaps_shop", "email")
    op.drop_column("weedmaps_shop", "business_hours")
    op.drop_column("weedmaps_shop", "announcement")
    op.drop_column("weedmaps_shop", "amenities")
    op.drop_column("weedmaps_shop", "aboutus")
    # ### end Alembic commands ###
