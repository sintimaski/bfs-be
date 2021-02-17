import json

from flask import Blueprint, render_template, request, abort
from core.blueprints.user import login_required
from sqlalchemy import asc

from core.db_connector import db
from core.consts import LISTING_CLASSES
from core.models import Business

listings_blueprint = Blueprint(
    "listings_blueprint", __name__, url_prefix="/listings"
)


@listings_blueprint.route("/api_listings/<project>", methods=["GET", "POST"])
def index(project):
    data = json.loads(request.data)
    page = int(data["page"])
    limit = int(data["limit"])
    records_rows = (
        Business.query.filter(Business.project == project)
        .limit(limit)
        .offset(page * limit)
        .all()
    )
    records = []
    for record_row in records_rows:
        records.append(record_row.as_dict())

    print(records)
    res = {"data": records}
    return res
