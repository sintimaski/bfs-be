from core.db_connector import db
from .base_model import BaseModel
from .gmaps_business import GmapsBusiness
from .weedmaps_shop import WeedmapsShop


class WeedMapping(db.Model, BaseModel):
    id = db.Column(db.Integer, primary_key=True)
    gmaps_id = db.Column(db.Integer, db.ForeignKey(GmapsBusiness.id))
    weedmaps_id = db.Column(db.Integer, db.ForeignKey(WeedmapsShop.id))
