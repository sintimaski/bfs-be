import json
from math import ceil

import cloudscraper
from flask import Blueprint, request
from sqlalchemy import asc, func, not_, cast, String

from core.db_connector import db
from core.models import Business, R2GBusiness


listings_blueprint = Blueprint(
    "listings_blueprint", __name__, url_prefix="/listings"
)


@listings_blueprint.route(
    "/api_listings/businesses/<project>", methods=["GET", "POST"]
)
def api_listings__businesses(project):
    data = json.loads(request.data)

    page = int(data["page"]) - 1
    page = max(0, page)
    limit = int(data["limit"])

    # BASIC QUERY
    records_rows_q = Business.query.filter(Business.project == project)
    total_q = db.session.query(func.count(Business.mapped)).group_by(
        Business.project
    )

    # FILTER
    records_rows_q = _apply_filters(records_rows_q, data, Business)
    total_q = _apply_filters(total_q, data, Business)

    records_rows_q = _filter_skipped_mapped(records_rows_q, data, Business)
    total_q = _filter_skipped_mapped(total_q, data, Business)

    # ADD LIMITS
    records_rows_q = (
        records_rows_q.order_by(asc(Business.id))
        .limit(limit)
        .offset(page * limit)
    )

    # FETCH
    records_rows = records_rows_q.all()
    total = total_q.scalar() or 0

    # FORMAT
    records = []
    for record_row in records_rows:
        records.append(record_row.as_dict())
    total_pages = int(ceil(total / limit))

    sources = (
        db.session.query(Business.source)
        .filter(R2GBusiness.project == project)
        .distinct(Business.source)
        .group_by(Business.source)
        .all()
    )
    sources = [source.source for source in sources]

    response = {
        "data": records,
        "total_pages": total_pages,
        "total": total,
        "sources": sources,
    }
    return response


@listings_blueprint.route(
    "/api_listings/r2g_businesses/<project>", methods=["GET", "POST"]
)
def api_listings__r2g_businesses(project):
    data = json.loads(request.data)

    page = int(data["page"]) - 1
    page = max(0, page)
    limit = int(data["limit"])

    # BASIC QUERY
    records_rows_q = R2GBusiness.query.filter(R2GBusiness.project == project)
    total_q = db.session.query(
        func.count(R2GBusiness.project).label("total")
    ).group_by(R2GBusiness.project)

    # FILTER
    records_rows_q = _apply_filters(records_rows_q, data, R2GBusiness)
    total_q = _apply_filters(total_q, data, R2GBusiness)

    # ADD LIMITS
    records_rows_q = (
        records_rows_q.order_by(asc(R2GBusiness.id))
        .limit(limit)
        .offset(page * limit)
    )

    # FETCH
    records_rows = records_rows_q.all()
    total = total_q.scalar() or 0

    # FORMAT
    records = []
    for record_row in records_rows:
        records.append(record_row.as_dict())
    total_pages = int(ceil(total / limit))

    res = {"data": records, "total_pages": total_pages, "total": total}
    return res


@listings_blueprint.route(
    "/api_listings/r2g_businesses/save/<project>", methods=["POST"]
)
def api_listings__save(project):
    data = request.get_json(force=True)
    edited = data.get("edited", {})
    business = R2GBusiness.query.filter(R2GBusiness.id == edited["id"]).first()
    edited.pop("id", None)
    for key, value in edited.items():
        setattr(business, key, value)
    db.session.commit()
    return {}


@listings_blueprint.route(
    "/api_listings/r2g_businesses/send/<project>", methods=["POST"]
)
def api_listings__send(project):
    data = request.get_json(force=True)
    to_send = data.get("toSend", {})

    target_business = R2GBusiness.query.filter(
        R2GBusiness.id == to_send["id"]
    ).first()

    business_hours = []
    try:
        for day, oph in target_business.business_hours.items():
            hours = {"open": oph["opens"], "close": oph["closes"]}
            business_hours.append({day.lower()[:3]: hours})
    except:
        pass

    province_mapping = {
        "Alberta": "AB",
        "British Columbia": "BC",
        "Manitoba": "MB",
        "New Brunswick": "NB",
        "Newfoundland and Labrador": "NL",
        "Nova Scotia": "NS",
        "Northwest Territories": "NT",
        "Nunavut": "NU",
        "Ontario": "ON",
        "AlbertaPrince Edward Island": "PE",
        "Quebec": "QC",
        "Saskatchewan": "SK",
        "Yukon": "YT",
        'Alabama': 'AL',
        'Alaska': 'AK',
        'Arizona': 'AZ',
        'Arkansas': 'AR',
        'California': 'CA',
        'Colorado': 'CO',
        'Connecticut': 'CT',
        'Delaware': 'DE',
        'District of Columbia': 'DC',
        'Florida': 'FL',
        'Georgia': 'GA',
        'Hawaii': 'HI',
        'Idaho': 'ID',
        'Illinois': 'IL',
        'Indiana': 'IN',
        'Iowa': 'IA',
        'Kansas': 'KS',
        'Kentucky': 'KY',
        'Louisiana': 'LA',
        'Maine': 'ME',
        'Maryland': 'MD',
        'Massachusetts': 'MA',
        'Michigan': 'MI',
        'Minnesota': 'MN',
        'Mississippi': 'MS',
        'Missouri': 'MO',
        'Montana': 'MT',
        'Nebraska': 'NE',
        'Nevada': 'NV',
        'New Hampshire': 'NH',
        'New Jersey': 'NJ',
        'New Mexico': 'NM',
        'New York': 'NY',
        'North Carolina': 'NC',
        'North Dakota': 'ND',
        'Ohio': 'OH',
        'Oklahoma': 'OK',
        'Oregon': 'OR',
        'Pennsylvania': 'PA',
        'Rhode Island': 'RI',
        'South Carolina': 'SC',
        'South Dakota': 'SD',
        'Tennessee': 'TN',
        'Texas': 'TX',
        'Utah': 'UT',
        'Vermont': 'VT',
        'Virginia': 'VA',
        'Washington': 'WA',
        'West Virginia': 'WV',
        'Wisconsin': 'WI',
        'Wyoming': 'WY',
    }
    province = (
        province_mapping.get(target_business.state, "UNKNOWN")
        if len(target_business.state) != 2 and target_business.country == 'CA'
        else target_business.state
    )
    category = (
        (target_business.category or "")
        if target_business.category != "dispensary"
        else "dispensaries"
    )

    scrapper = cloudscraper.create_scraper()
    headers = {"Content-type": "application/json"}

    status = "publish"
    target_id = target_business.target_id or ""
    if target_id:
        resp = scrapper.post(
            f"https://trinity.justwebagency.com/magazine/"
            f"wp-json/jwa-locator/v1/location/{target_id}",
            headers=headers,
        )
        resp = json.loads(resp.text)
        status = resp.get("status", "publish")

    phone = target_business.phone or ""
    phone = f"{phone[:3]}-{phone[3:6]}-{phone[6:10]}"
    rest_data = {
        "title": target_business.name or "",
        "status": status,
        "address": target_business.address or "",
        "city": [{"name": target_business.city or ""}],
        "country": target_business.country or "",
        "province": [{"name": province or ""}],
        "postal_code": target_business.zip or "",
        "lat": target_business.lat or "",
        "lng": target_business.lng or "",
        "phone": phone,
        "web_site": target_business.website or "",
        "open_hours": business_hours,
        "about": target_business.about or "",
        "soc": [],
        "logo": target_business.logo or "",
        "gallery": target_business.gallery or [],
        "reviews": [],
        "category": category,
        "tag": target_business.subcategory or "",
    }

    rest_data.update({"token": "xWgbfKYZvX6aEFvK"})

    resp = scrapper.post(
        f"https://trinity.justwebagency.com/magazine/"
        f"wp-json/jwa-locator/v1/location/{target_id}",
        json=rest_data,
        headers=headers,
    )
    print(resp.text)

    if resp.status_code != 200:
        return {"error": "Something went wrong..."}

    resp_json = json.loads(resp.text)
    target_business.target_link = resp_json.get("link", "")
    target_business.target_id = resp_json.get("locationID", "")
    db.session.commit()

    return {}


def _apply_filters(query, data, cls):
    for key, value in data["filters"].items():
        attr = getattr(cls, key)
        if value:
            query = query.filter(cast(attr, String).ilike(f"%{value.strip()}%"))
    return query


def _filter_skipped_mapped(query, data, cls):
    skipped_mapped = data.get("skipped_mapped")
    if skipped_mapped == "skipped":
        query = query.filter(cls.skipped.is_(True))
    elif skipped_mapped == "not_skipped":
        query = query.filter(not_(cls.mapped))
    elif skipped_mapped == "mapped":
        query = query.filter(cls.mapped.is_(True))
    elif skipped_mapped == "not_mapped":
        query = query.filter(not_(cls.mapped))
    return query
