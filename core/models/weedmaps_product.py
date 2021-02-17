from sqlalchemy.dialects.postgresql import ARRAY

from core.db_connector import db
from .base_model import BaseModel


class WeedmapsProduct(db.Model, BaseModel):
    id = db.Column(db.Integer, primary_key=True)
    weedmaps_id = db.Column(db.String(25), nullable=True)
    shop_slug = db.Column(db.Text(), nullable=True)
    name = db.Column(db.Text(), nullable=False)
    category = db.Column(db.String(255), nullable=False)
    image_url = db.Column(db.Text(), nullable=False)
    description = db.Column(db.Text(), nullable=True)
    short_description = db.Column(db.Text(), nullable=True)
    prices = db.Column(ARRAY(db.String(25)), nullable=True)
    prices_labels = db.Column(ARRAY(db.String(25)), nullable=True)
    price_unit = db.Column(db.String(25), nullable=False)
    strain_effects = db.Column(ARRAY(db.String(25)), nullable=True)
    strain_flavours = db.Column(ARRAY(db.String(25)), nullable=True)
    web_url = db.Column(db.Text(), nullable=False)
    details_collected = db.Column(db.Boolean, default=False)
