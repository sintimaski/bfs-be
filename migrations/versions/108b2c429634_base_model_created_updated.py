"""Base model + created + updated

Revision ID: 108b2c429634
Revises: 76fb82b8961b
Create Date: 2020-09-24 04:03:24.748746

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "108b2c429634"
down_revision = "76fb82b8961b"
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table("base_model")
    op.add_column(
        "car_product", sa.Column("created_at", sa.DateTime(), nullable=True)
    )
    op.add_column(
        "car_product", sa.Column("source_id", sa.Text(), nullable=True)
    )
    op.add_column(
        "car_product", sa.Column("updated_at", sa.DateTime(), nullable=True)
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column("car_product", "updated_at")
    op.drop_column("car_product", "source_id")
    op.drop_column("car_product", "created_at")
    op.create_table(
        "base_model",
        sa.Column("id", sa.INTEGER(), autoincrement=True, nullable=False),
        sa.Column(
            "created_at",
            postgresql.TIMESTAMP(),
            autoincrement=False,
            nullable=True,
        ),
        sa.Column(
            "updated_at",
            postgresql.TIMESTAMP(),
            autoincrement=False,
            nullable=True,
        ),
        sa.Column("source", sa.TEXT(), autoincrement=False, nullable=True),
        sa.Column("source_id", sa.TEXT(), autoincrement=False, nullable=True),
        sa.Column(
            "product_name", sa.TEXT(), autoincrement=False, nullable=True
        ),
        sa.Column("price", sa.TEXT(), autoincrement=False, nullable=True),
        sa.Column("condition", sa.TEXT(), autoincrement=False, nullable=True),
        sa.Column(
            "images",
            postgresql.ARRAY(sa.TEXT()),
            autoincrement=False,
            nullable=True,
        ),
        sa.Column("make", sa.TEXT(), autoincrement=False, nullable=True),
        sa.Column("model", sa.TEXT(), autoincrement=False, nullable=True),
        sa.Column("year", sa.TEXT(), autoincrement=False, nullable=True),
        sa.Column("body_style", sa.TEXT(), autoincrement=False, nullable=True),
        sa.Column("odometer", sa.TEXT(), autoincrement=False, nullable=True),
        sa.Column(
            "transmission", sa.TEXT(), autoincrement=False, nullable=True
        ),
        sa.Column("engine", sa.TEXT(), autoincrement=False, nullable=True),
        sa.Column("engine_size", sa.TEXT(), autoincrement=False, nullable=True),
        sa.Column("driveline", sa.TEXT(), autoincrement=False, nullable=True),
        sa.Column(
            "exterior_color", sa.TEXT(), autoincrement=False, nullable=True
        ),
        sa.Column(
            "interior_color", sa.TEXT(), autoincrement=False, nullable=True
        ),
        sa.Column("doors", sa.TEXT(), autoincrement=False, nullable=True),
        sa.Column("passengers", sa.TEXT(), autoincrement=False, nullable=True),
        sa.Column("fuel", sa.TEXT(), autoincrement=False, nullable=True),
        sa.Column("city_fuel", sa.TEXT(), autoincrement=False, nullable=True),
        sa.Column("hwy_fuel", sa.TEXT(), autoincrement=False, nullable=True),
        sa.Column(
            "stock_number", sa.TEXT(), autoincrement=False, nullable=True
        ),
        sa.Column("vin", sa.TEXT(), autoincrement=False, nullable=True),
        sa.Column("details", sa.TEXT(), autoincrement=False, nullable=True),
        sa.Column(
            "options",
            postgresql.JSON(astext_type=sa.Text()),
            autoincrement=False,
            nullable=True,
        ),
        sa.Column("content", sa.TEXT(), autoincrement=False, nullable=True),
        sa.Column("web_url", sa.TEXT(), autoincrement=False, nullable=True),
        sa.Column(
            "location_diller", sa.TEXT(), autoincrement=False, nullable=True
        ),
        sa.PrimaryKeyConstraint("id", name="base_model_pkey"),
    )
    # ### end Alembic commands ###
