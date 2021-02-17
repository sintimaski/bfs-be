import csv


def csv_exporter(model, filename, fieldnames=None):
    if not fieldnames:
        fieldnames = []

    entites = model.query.all()
    with open(filename, "w+") as file:
        formatted = []
        for entity in entites:
            ff = {}
            for key, value in entity.as_dict().items():
                if key in fieldnames or not fieldnames:
                    ff.update(
                        {
                            key: value,
                        }
                    )
            formatted.append(ff)
        writer = csv.DictWriter(
            file, fieldnames=fieldnames, quoting=csv.QUOTE_ALL
        )
        writer.writeheader()
        writer.writerows(formatted)


def export_to_csv():
    import csv
    from core.models import WeedmapsProduct

    products = WeedmapsProduct.query.all()
    formatted = []
    for product in products:
        strain_effects = "|".join(product.strain_effects)
        strain_flavours = "|".join(product.strain_flavours)
        formatted.append(
            {
                "name": product.name,
                "category": product.category,
                "image_url": product.image_url,
                "prices": "|".join(product.prices),
                "prices_labels": "|".join(product.prices_labels),
                "price_unit": product.price_unit,
                "description": product.description,
                "short_description": product.short_description,
                "strain_effects": strain_effects,
                "strain_flavours": strain_flavours,
            }
        )
    with open("files/king_crop.csv", "w+") as filew:
        fnames = [
            "name",
            "category",
            "image_url",
            "prices",
            "prices_labels",
            "price_unit",
            "description",
            "short_description",
            "strain_effects",
            "strain_flavours",
        ]
        writer = csv.DictWriter(filew, fieldnames=fnames, quoting=csv.QUOTE_ALL)
        writer.writeheader()
        writer.writerows(formatted)
