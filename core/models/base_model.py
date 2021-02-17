from collections import OrderedDict
from datetime import datetime

from flask import abort

from core.db_connector import db


class BaseModel(object):
    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.DateTime, default=datetime.now)
    updated_at = db.Column(
        db.DateTime, default=datetime.now, onupdate=datetime.now
    )
    _repr_hide = ["created_at", "updated_at"]

    def as_dict(self):
        result = OrderedDict()
        for key in self.__mapper__.c.keys():
            result[key] = getattr(self, key)
        return result

    @classmethod
    def query(cls):
        return db.session.query(cls)

    @classmethod
    def get(cls, id):
        return cls.query.get(id)

    @classmethod
    def get_by(cls, **kw):
        return cls.query.filter_by(**kw).first()

    @classmethod
    def get_or_404(cls, id):
        rv = cls.get(id)
        if rv is None:
            abort(404)
        return rv

    @classmethod
    def get_or_create(cls, **kw):
        r = cls.get_by(**kw)
        if not r:
            r = cls(**kw)
            db.session.add(r)

        return r

    @classmethod
    def create(cls, **kw):
        r = cls(**kw)
        db.session.add(r)
        return r

    def save(self):
        db.session.add(self)

    def delete(self):
        db.session.delete(self)

    def __repr__(self):
        values = ", ".join(
            "%s=%r" % (n, getattr(self, n))
            for n in self.__table__.c.keys()
            if n not in self._repr_hide
        )
        return "%s(%s)" % (self.__class__.__name__, values)

    def filter_string(self):
        return self.__str__()
