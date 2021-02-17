import json

from flask import Blueprint, request
from flask import Response
from sqlalchemy import func, asc, and_, not_

from core.db_connector import db
from core.models import Business, R2GBusiness

mapper_blueprint = Blueprint("mapper_blueprint", __name__, url_prefix="/mapper")


def get_all_available_sources(project, remove_list=None):
    q = (
        db.session.query(
            Business.source, func.count(Business.mapped).label("total_unmapped")
        )
        .filter(
            and_(
                Business.project == project,
                not_(Business.mapped),
                not_(Business.skipped),
            )
        )
        .group_by(Business.source)
    )
    if remove_list:
        q = q.filter(Business.source.notin_(remove_list))
    all_sources = q.all()
    return all_sources


@mapper_blueprint.route("/api_mapper/save/<project>", methods=["POST"])
def api_mapper__save(project):
    data = json.loads(request.data)
    new_business = R2GBusiness(
        project=project,
        name=data["name"],
        tag=data["tag"],
        category=data["category"],
        business_hours=data["business_hours"],
        soc_fb=data["soc_fb"],
        soc_tw=data["soc_tw"],
        soc_in=data["soc_in"],
        website=data["website"],
        email=data["email"],
        phone=data["phone"],
        country=data["country"],
        address=data["address"],
        city=data["city"],
        zip=data["zip"],
        about=data["about"],
        gallery=data["gallery"],
    )
    db.session.add(new_business)
    db.session.commit()

    for idx in data["ids"]:
        if idx:
            used = Business.query.filter(Business.id == str(idx)).first()
            used.mapped = True
            used.mapped_to_id = new_business.id
            db.session.commit()
    return {}


@mapper_blueprint.route("/api_mapper/search/<project>", methods=["POST"])
def api_mapper__search(project):
    data = json.loads(request.data)
    locked = data.pop("lockedSources", None)
    other_sources = get_all_available_sources(project, remove_list=locked)
    # other_sources = [source.source for source in other_sources]
    q = (
        db.session.query(Business)
        .filter(
            and_(
                Business.project == project,
                not_(Business.mapped),
            )
        )
        .order_by(asc(Business.order_in_mapping_queue))
    )
    for key, value in data.items():
        attr = getattr(Business, key)
        if value:
            q = q.filter(attr.ilike(f"%{value.strip()}%"))

    results = []
    for source in other_sources:
        curr_q = q.filter(Business.source == source.source)
        businesses_found = curr_q.all()
        if businesses_found:
            business = businesses_found[0]

            business.order_in_mapping_queue += 1
            db.session.commit()

            business = business.as_dict()
            business.update(
                {
                    "total_found": len(businesses_found),
                    "total_unmapped": source.total_unmapped,
                }
            )
            results.append(business)
    return {"results": results}


@mapper_blueprint.route("/api_mapper/next/<project>", methods=["GET"])
def api_mapper__next(project):
    needed_source = (
        db.session.query(Business.source)
        .filter(
            and_(
                Business.project == project,
                not_(Business.mapped),
                not_(Business.skipped),
            )
        )
        .group_by(Business.source)
        .order_by(asc(func.count(Business.source)))
        .first()
    )
    if not needed_source:
        return {"error": {"No available businesses"}}
    needed_source = needed_source.source

    next_business = (
        db.session.query(Business)
        .filter(
            and_(
                Business.project == project,
                Business.source == needed_source,
                not_(Business.mapped),
                not_(Business.skipped),
            )
        )
        .order_by(asc(Business.order_in_mapping_queue))
        .first()
    )

    if not next_business:
        return Response(
            {"error": {"No available businesses"}},
            status=404,
            mimetype="application/json",
        )
    next_business.order_in_mapping_queue += 1
    db.session.commit()
    next_business = next_business.as_dict()
    next_business.pop("created_at", None)
    next_business.pop("updated_at", None)
    next_business["main"] = "true"

    all_sources = get_all_available_sources(project)

    template = {}
    for key, value in next_business.items():
        next_business[key] = next_business[key] or ""
        template.update({key: ""})
    businesses = []
    for source in all_sources:
        business = (
            template.copy() if source.source != needed_source else next_business
        )
        business.update(
            {
                "source": source.source,
                "total_unmapped": source.total_unmapped,
                "main": source.source == needed_source,
            }
        )
        businesses.append(business)

    result = template.copy()
    result.update({"source": "ResultSource", "result_source": True})
    businesses.append(result)

    resp = {
        "businesses": businesses,
    }
    return Response(json.dumps(resp), status=200, mimetype="application/json")


@mapper_blueprint.route("/api_mapper/skip/<project>", methods=["POST"])
def api_mapper__skip(project):
    data = json.loads(request.data)
    business = Business.query.filter(Business.id == data["id"]).first()
    business.skipped = True
    db.session.commit()
    return Response("", status=200, mimetype="application/json")
