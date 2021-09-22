from datetime import datetime

from sqlalchemy.orm.attributes import flag_modified
from sqlalchemy.dialects.postgresql import JSON, ARRAY
from sqlalchemy.event import listens_for

from core.db_connector import db
from .base_model import BaseModel
from ..redis_tasker import redis_queue


class Business(db.Model, BaseModel):
    id = db.Column(db.Integer, primary_key=True)
    source_name__id = db.Column(db.Text())
    project = db.Column(db.Text())
    name = db.Column(db.Text())
    source = db.Column(db.Text())
    category = db.Column(db.Text())
    subcategory = db.Column(db.Text())
    tag = db.Column(db.Text())
    business_hours = db.Column(JSON())
    web_url = db.Column(db.Text())
    slug = db.Column(db.Text())

    soc_fb = db.Column(db.Text())
    soc_tw = db.Column(db.Text())
    soc_in = db.Column(db.Text())
    soc_ig = db.Column(db.Text())
    website = db.Column(db.Text())
    email = db.Column(db.Text())
    phone = db.Column(db.Text())

    country = db.Column(db.Text())
    state = db.Column(db.Text())
    city = db.Column(db.Text())
    address = db.Column(db.Text())
    address_2 = db.Column(db.Text())
    zip = db.Column(db.Text())
    lat = db.Column(db.Text())
    lng = db.Column(db.Text())

    about = db.Column(db.Text())
    gallery = db.Column(ARRAY(db.Text()))

    mapped = db.Column(db.Boolean(), default=False)
    mapped_to_id = db.Column(db.Integer)
    order_in_mapping_queue = db.Column(db.Integer, default=0)
    skipped = db.Column(db.Boolean(), default=False)


@listens_for(Business, "before_update")
def filter_values(mapper, connect, target):
    target.phone = filter_phone(target.phone)
    target.website = filter_website(target.website)
    target.business_hours = filter_hours(target.business_hours, target.source)
    redis_queue.enqueue(check_for_updates, target)


@listens_for(Business, "before_insert")
def filter_values(mapper, connect, target):
    target.phone = filter_phone(target.phone)
    target.website = filter_website(target.website)
    target.business_hours = filter_hours(target.business_hours, target.source)


def filter_phone(phone):
    phone = "" if not phone else phone
    phone = [c for c in phone if c.isdigit()]
    if len(phone) > 10:
        phone = phone[len(phone) - 10:]
    phone = "".join(phone)
    return phone


def filter_website(website):
    if not website:
        return ""
    website = website.strip("/")
    website = website.lower()
    website = website.replace("//", "")
    website = website.replace("http:", "")
    website = website.replace("https:", "")
    website = website.replace("www.", "")
    website = website.split("?", 1)[0]
    website = website.split("/", 1)[0]
    return website


def filter_hours(hours, source):
    if not hours:
        return {}
    formatted_hours = {}
    try:
        if source == "gmaps":
            for day, opcl in hours.items():
                if opcl == "Closed":
                    opens = "closed"
                    closes = "closed"
                elif opcl == "Open 24 hours":
                    opens = "00:00"
                    closes = "24:00"
                else:
                    opens = opcl.split("–")[0]
                    opens = (
                        opens if opens.endswith(("AM", "PM")) else f"{opens}PM"
                    )
                    closes = opcl.split("–")[1]
                    closes = (
                        closes
                        if closes.endswith(("AM", "PM"))
                        else f"{closes}AM"
                    )
                    opens = _format_to_24(opens)
                    closes = _format_to_24(closes)

                formatted_hours.update(
                    {
                        day.lower(): {
                            "opens": opens,
                            "closes": closes,
                        }
                    }
                )
            return formatted_hours
        elif source == "weedmaps":
            for day, _hours in hours.items():
                formatted_hours.update(
                    {
                        day: {
                            "opens": _format_to_24(_hours["open"].upper()),
                            "closes": _format_to_24(_hours["close"].upper()),
                        }
                    }
                )
            return formatted_hours
        elif source == "leafly":
            if hours == "null":
                return {}
            for day, opcl in hours.items():
                opens = (
                    opcl["open"]
                    .replace(":00.000Z", "")
                    .replace(":00Z", "")
                    .replace("Z", "")
                )
                closes = (
                    opcl["close"]
                    .replace(":00.000Z", "")
                    .replace(":00Z", "")
                    .replace("Z", "")
                )
                if "T" in opens:
                    opens = opcl["open"].split("T")[1]
                if "T" in closes:
                    closes = opcl["close"].split("T")[1]

                formatted_hours.update(
                    {
                        day: {
                            "opens": opens if opcl["isOpen"] else "closed",
                            "closes": closes if opcl["isOpen"] else "closed",
                        }
                    }
                )
            return formatted_hours
    except:
        return hours
    return hours


def _format_to_24(m2):
    template = "%I:%M%p" if ":" in m2 else "%I%p"
    in_time = datetime.strptime(m2, template)
    out_time = datetime.strftime(in_time, "%H:%M")
    return out_time


def check_for_updates(target):
    from app import app
    from core.models.r2g_business import R2GBusiness
    from core.db_connector import db

    needs_check = False
    to_check = ["website", "phone", "business_hours"]
    with app.app_context():
        r2g_business = R2GBusiness.query.filter(
            R2GBusiness.id == target.mapped_to_id
        ).first()
        if r2g_business:
            last_update = r2g_business.last_update or {}
            source_update = last_update.get(target.source, {})
            new_source_update = source_update
            for field in to_check:
                if field in source_update:
                    last_value = source_update.get(field, None)
                else:
                    last_value = getattr(r2g_business, field)
                new_value = getattr(target, field)

                if isinstance(new_value, dict) or isinstance(last_value, dict):
                    new_value = new_value or {}
                    last_value = last_value or {}
                    for key in new_value:
                        if (key not in last_value or last_value[key] !=
                                new_value[key]):
                            new_source_update.update({field: new_value})
                            needs_check = True
                            break
                elif new_value != last_value:
                    needs_check = True
                    new_source_update.update({field: new_value})

            new_last_update = last_update
            new_last_update.update({
                target.source: new_source_update
            })
            r2g_business.last_update = last_update
            flag_modified(r2g_business, "last_update")
            if not r2g_business.needs_check:
                r2g_business.needs_check = needs_check
            db.session.commit()
