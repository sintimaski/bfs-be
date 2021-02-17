from sqlalchemy.dialects.postgresql import JSON, ARRAY

from core.db_connector import db
from .base_model import BaseModel


class Business(db.Model, BaseModel):
    id = db.Column(db.Integer, primary_key=True)
    project = db.Column(db.Text())
    name = db.Column(db.Text())
    source = db.Column(db.Text())
    category = db.Column(db.Text())
    subcategory = db.Column(db.Text())
    tag = db.Column(db.Text())
    business_hours = db.Column(JSON())
    web_url = db.Column(db.Text())
    slug = db.Column(db.Text())

    soc_fb = db.Column(db.Text())
    soc_tw = db.Column(db.Text())
    soc_in = db.Column(db.Text())
    website = db.Column(db.Text())
    email = db.Column(db.Text())
    phone = db.Column(db.Text())

    country = db.Column(db.Text())
    state = db.Column(db.Text())
    city = db.Column(db.Text())
    address = db.Column(db.Text())
    address_2 = db.Column(db.Text())
    zip = db.Column(db.Text())
    lat = db.Column(db.Text())
    lng = db.Column(db.Text())

    about = db.Column(db.Text())
    gallery = db.Column(ARRAY(db.Text()))

    mapped = db.Column(db.Boolean(), default=False)
    mapped_to_id = db.Column(db.Integer)
    order_in_mapping_queue = db.Column(db.Integer, default=0)
    skipped = db.Column(db.Boolean(), default=False)
