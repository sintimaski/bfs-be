import json

from flask import Blueprint, request
from flask import Response
from sqlalchemy import and_

# from app import app
from core.db_connector import db
from core.models import R2GBusiness

updater_blueprint = Blueprint(
    "updater_blueprint", __name__, url_prefix="/updater"
)


@updater_blueprint.route("/api_updater/save/<project>", methods=["POST"])
def api_mapper__save(project):
    data = request.get_json(force=True)
    business = R2GBusiness.query.filter(R2GBusiness.id == data["id"]).first()
    data.pop("id", None)
    for key, value in data.items():
        setattr(business, key, value)
    db.session.commit()
    return {}


@updater_blueprint.route("/api_updater/next/<project>", methods=["GET"])
def api_mapper__next(project):
    business = R2GBusiness.query.filter(
        and_(R2GBusiness.project == project, R2GBusiness.needs_check)
    ).first()
    if business:
        business = business.__dict__
        business.pop("_sa_instance_state")
        business.pop("created_at")
        business.pop("updated_at")
    else:
        business = {}
    return Response(
        json.dumps(business), status=200, mimetype="application/json"
    )
