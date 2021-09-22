import json

import cloudscraper
from flask import Blueprint, request, abort
from sqlalchemy import asc, func, not_, cast, String

from core.blueprints.user import login_required
from core.consts import ROLE_ADMIN
from core.db_connector import db
from core.models import Business, R2GBusiness, Preset

presets_blueprint = Blueprint(
    "presets_blueprint", __name__, url_prefix="/presets"
)


@login_required(ROLE_ADMIN)
@presets_blueprint.route(
    "/api_presets", methods=["GET"]
)
@presets_blueprint.route(
    "/api_presets/<name>", methods=["GET"]
)
def api_presets(name=None):
    if name:
        preset = Preset.query.filter(Preset.name == name).first()
        if not preset:
            return {'result': {}}
        preset = preset.as_dict()
        return {'result': preset}
    else:
        _presets = Preset.query.all()
        presets = []
        for preset in _presets:
            presets.append(preset.as_dict())
        return {'result': presets}


@login_required(ROLE_ADMIN)
@presets_blueprint.route(
    "/api_presets/post", methods=["POST"]
)
def api_presets__post():
    data = request.get_json(force=True)
    edited = data.get("edited", {})

    if edited.get('id'):
        preset = Preset.query.filter(Preset.id == edited["id"]).first()
        preset.name = edited['name']
        preset.values = edited['values']
        db.session.commit()
    else:
        new_preset = Preset(
            name=edited['name'],
            values=edited['values'],
        )
        db.session.add(new_preset)
        db.session.commit()
    return {}


@login_required(ROLE_ADMIN)
@presets_blueprint.route(
    "/api_presets/delete", methods=["POST"]
)
def api_presets__delete():
    data = request.get_json(force=True)
    to_delete = data.get("toDelete", {})
    Preset.query.filter(Preset.id == to_delete['id']).delete()
    db.session.commit()
    return {}
