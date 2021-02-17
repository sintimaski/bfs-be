from core.db_connector import db
from .base_model import BaseModel
from sqlalchemy.dialects.postgresql import JSON


class ThirdParty(db.Model, BaseModel):
    name = db.Column(db.Text())
    username = db.Column(db.Text())
    password = db.Column(db.Text())
    api_key = db.Column(db.Text())
    url = db.Column(db.Text())
    data = db.Column(JSON())
