from sqlalchemy.dialects.postgresql import JSON, ARRAY

from core.db_connector import db
from .base_model import BaseModel


class GmapsBusiness(db.Model, BaseModel):
    # common
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Text())
    hours = db.Column(JSON())
    address_1 = db.Column(db.Text())
    address_2 = db.Column(db.Text())
    country = db.Column(db.Text())
    state = db.Column(db.Text())
    zip = db.Column(db.Text())
    phone = db.Column(db.Text())
    website = db.Column(db.Text())

    # unique
    gmaps_id = db.Column(db.Text())
    search_query = db.Column(db.Text())
    coordinates = db.Column(db.Text())
    categories = db.Column(ARRAY(db.Text()))
    status = db.Column(db.Text())
    image = db.Column(db.Text())

    # deprecated
    project = db.Column(db.Text())
    weed_mapping_id = db.relationship(
        "WeedMapping", uselist=False, backref="gmaps"
    )
    order_in_mapping_queue = db.Column(db.Integer, default=0)
