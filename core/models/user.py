from flask_login import UserMixin
from sqlalchemy.dialects.postgresql import ARRAY
from werkzeug.security import generate_password_hash, check_password_hash

from core.db_connector import db
from .base_model import BaseModel


class User(UserMixin, db.Model, BaseModel):
    username = db.Column(db.Text())
    first_name = db.Column(db.Text())
    last_name = db.Column(db.Text())
    email = db.Column(db.Text())
    password_hash = db.Column(db.Text())
    role = db.Column(db.Text())
    permissions = db.Column(ARRAY(db.Text()))

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
