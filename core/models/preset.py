from sqlalchemy.dialects.postgresql import ARRAY

from core.db_connector import db
from .base_model import BaseModel


class Preset(db.Model, BaseModel):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Text())
    values = db.Column(ARRAY(db.Text()))
