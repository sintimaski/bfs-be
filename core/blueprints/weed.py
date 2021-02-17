import json

from flask import Blueprint, render_template, request
from core.blueprints.user import login_required
from sqlalchemy import asc

from core.db_connector import db
from core.models import GmapsBusiness, WeedMapping, WeedmapsShop

weed_blueprint = Blueprint("weed_blueprint", __name__, url_prefix="/weed")


@weed_blueprint.route("/", methods=["GET"])
@login_required()
def index():
    gmaps_count = GmapsBusiness.query.count()
    return render_template("weed.html", gmaps_count=gmaps_count)


@weed_blueprint.route("/api_weed/search/<resource>/", methods=["POST"])
@login_required()
def api_weed_search(resource):
    resources = {
        "weedmaps": WeedmapsShop,
        "gmaps": GmapsBusiness,
    }

    resource = resources[resource]
    data = json.loads(request.data)
    target = data["target"]
    value = data["value"]
    entity = resource.query.filter(
        getattr(resource, target).like(f"%{value}%")
    ).first()
    if entity:
        resp = entity.as_dict()
    else:
        resp = {}
    return resp


@weed_blueprint.route("/api_weed/next", methods=["GET"])
@login_required()
def api_weed__next():
    # TODO add ms schemas
    mapped = WeedMapping.query.all()
    gmaps_mapped = []
    weedmaps_mapped = []
    for entiny in mapped:
        gmaps_mapped.append(entiny.gmaps_id)
        weedmaps_mapped.append(entiny.weedmaps_id)

    gmaps_first = (
        GmapsBusiness.query.filter(GmapsBusiness.id.notin_(gmaps_mapped))
        .order_by(asc(GmapsBusiness.order_in_mapping_queue))
        .first()
    )
    gmaps_first.order_in_mapping_queue += 1
    db.session.commit()

    resp = {"resources": [{"name": "gmaps", "data": gmaps_first.as_dict()}]}
    return resp


def _get_most_similar():
    from core.models import GmapsBusiness, WeedmapsShop

    from difflib import SequenceMatcher
    import numpy as np
    import itertools

    similarity = lambda x: np.mean(
        [
            SequenceMatcher(None, a, b).ratio()
            for a, b in itertools.combinations(x, 2)
        ]
    )

    gms = GmapsBusiness.query.all()
    wms = WeedmapsShop.query.all()

    for gm in gms[50:]:
        selected = {}
        for wm in wms:

            def make_simple_string(s):
                s = s.replace("https://", "")
                s = s.replace("http://", "")
                s = "".join([u for u in s if u.isalpha()])
                return s

            def make_simple_number(n):
                n = "".join([p for p in n if p.isnumeric()])
                return n

            website_similarity = similarity(
                [
                    make_simple_string(gm.website or ""),
                    make_simple_string(wm.business_name or ""),
                ]
            )
            phone_similarity = similarity(
                [
                    make_simple_number(gm.phone or ""),
                    make_simple_number(wm.phone or ""),
                ]
            )
            address_similarity = similarity(
                [
                    gm.address_1 or "",
                    wm.address or "",
                ]
            )
            name_similarity = similarity(
                [
                    gm.name or "",
                    wm.business_name or "",
                ]
            )
            sims = [
                website_similarity,
                name_similarity,
                phone_similarity,
                address_similarity,
            ]
            total_similarity = sum(sims) / len(sims)
            if total_similarity > selected.get("total_similarity", 0):
                selected.update(
                    {
                        "gm": gm.as_dict(),
                        "wm": wm.as_dict(),
                        "total_similarity": total_similarity,
                    }
                )
        if selected["total_similarity"] > 0.65:
            from pprint import pprint

            pprint(selected)
            break
        else:
            print(selected["total_similarity"])
