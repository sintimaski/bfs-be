def get_text_by_sibling_text(soup, span_text, sibling_tag="span") -> str:
    sibling = soup.find(
        lambda tag: tag.name == sibling_tag and span_text in tag.text
    )
    text = ""
    if sibling:
        parent = sibling.parent
        sibling.extract()
        try:
            text = parent.text
        finally:
            pass
    return text


def delete_duplicates():
    from core.models import CarProduct
    from core.db_connector import db

    entities = CarProduct.query.all()
    data = {}
    for entity in entities:
        idx = data.get(entity.vin, None)
        if idx:
            if entity.id > idx:
                data.update({entity.vin: entity.id})
        else:
            data.update({entity.vin: entity.id})

    from sqlalchemy import and_

    for vin, idx in data.items():
        cars = CarProduct.query.filter(
            and_(CarProduct.vin == vin, CarProduct.id != idx)
        ).all()
        for car in cars:
            db.session.delete(car)
        db.session.commit()
