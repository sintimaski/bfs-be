from sqlalchemy.dialects.postgresql import ARRAY, JSON

from core.db_connector import db
from .base_model import BaseModel


class WeedmapsShop(db.Model, BaseModel):
    # common
    id = db.Column(db.Integer, primary_key=True)
    business_name = db.Column(db.Text(), nullable=False)
    city = db.Column(db.Text(), nullable=True)
    address = db.Column(db.Text(), nullable=True)
    web_url = db.Column(db.Text(), nullable=False)
    phone = db.Column(db.Text(), nullable=True)
    website = db.Column(db.Text(), nullable=True)
    business_hours = db.Column(JSON, nullable=True)
    email = db.Column(db.Text(), nullable=True)

    # likely common
    slug = db.Column(db.Text(), nullable=False)

    # unique
    weedmaps_id = db.Column(db.String(25), nullable=False, unique=True)
    type = db.Column(db.String(25), nullable=False)
    category = db.Column(db.String(25), nullable=False)
    intro = db.Column(db.Text(), nullable=True)
    services = db.Column(db.Text(), nullable=True)
    aboutus = db.Column(db.Text(), nullable=True)
    amenities = db.Column(ARRAY(db.Text()), nullable=True)
    f_t_announcement = db.Column(db.Text(), nullable=True)
    announcement = db.Column(db.Text(), nullable=True)

    # deprecated
    weed_mapping_id = db.relationship(
        "WeedMapping", uselist=False, backref="weedmaps"
    )
    order_in_mapping_queue = db.Column(db.Integer, default=0)
