import csv
import datetime
import json
import uuid

import boto3
import cloudscraper
import requests
from flask import Flask, redirect
from flask_cors import CORS
from sqlalchemy import and_

from core.blueprints import weed_blueprint, user_blueprint, listings_blueprint
from core.blueprints.mapper import mapper_blueprint
from core.blueprints.user import login_manager, login_required
from core.db_connector import db, migrate
from core.models import import_db_models, CarProduct


# from loguru import logger
# logger.add(sys.stderr, format="{time} {level} {message}",
#            filter="my_module", level="INFO", rotation="50 MB", colorize=True)


def create_app():
    # Create app.
    new_app = Flask(
        __name__, instance_relative_config=True, static_folder="static"
    )
    new_app.config.from_pyfile("flask.cfg")
    new_app.config["CORS_HEADERS"] = "Content-Type"

    # Register blueprints.
    new_app.register_blueprint(weed_blueprint)
    new_app.register_blueprint(user_blueprint)
    new_app.register_blueprint(listings_blueprint)
    new_app.register_blueprint(mapper_blueprint)

    # Import models, init DB.
    import_db_models()
    db.init_app(new_app)
    with new_app.app_context():
        db.create_all()
        db.session.commit()
    new_app.app_context().push()

    # Initialize migrations.
    migrate.init_app(new_app, db)

    # Initialize login.
    login_manager.init_app(new_app)

    # Add cors.
    CORS(new_app)

    return new_app


app = create_app()


@app.context_processor
def inject_template_globals():
    return {
        "nowts": datetime.datetime.utcnow(),
    }


@login_required
@app.route("/")
def index():
    return redirect("/weed")


# TODO Finish weedmaps scrapper
if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True)

    # from scrappers.cars.carnance import CarnanceScrapper
    # scrapper = CarnanceScrapper()
    # scrapper.start_routine()

    # from core.models import Business
    #
    # businesses = (
    #     Business.query.filter(Business.source == "gmaps").limit(150).all()
    # )
    # formatted = []
    # for business in businesses:
    #     business_hours = []
    #     if isinstance(business.business_hours, dict):
    #         for day, oph in business.business_hours.items():
    #             hours = {}
    #             if oph == "Closed":
    #                 am = "Close"
    #                 pm = "Close"
    #             elif oph == "Open 24 hours":
    #                 am = '00'
    #                 pm = '00'
    #             else:
    #                 am = oph.split("–")[0].strip("AM").strip("PM")
    #                 pm = oph.split("–")[1].strip("PM").strip("AM")
    #             hours = {"am": am, "pm": pm}
    #             business_hours.append({day.lower()[:3]: hours})
    #     formatted.append(
    #         {
    #             "title": business.name,
    #             "address": business.address,
    #             "city": business.city,
    #             "country": business.country,
    #             "province": business.state,
    #             "postal_code": business.zip,
    #             "lat": business.lat,
    #             "lng": business.lng,
    #             "phone": business.phone,
    #             "web_site": business.website,
    #             "open_hours": business_hours,
    #             "about": business.about,
    #             "soc": [],
    #             "gallery": business.gallery,
    #             "reviews": [],
    #             "category": business.category,
    #             "tag": business.subcategory,
    #         }
    #     )
    #
    # scrapper = cloudscraper.create_scraper()
    # passed = 0
    # for car_data in formatted:
    #     car_data.update({"token": "xWgbfKYZvX6aEFvK"})
    #     headers = {"Content-type": "application/json"}
    #     resp = scrapper.post(
    #         "https://thompson.justwebagency.com/magazine/wp-json/jwa-locator/v1/location",
    #         json=car_data,
    #         headers=headers,
    #     )
    #     passed += 1
    #     print(f"{passed}/{len(formatted)} {resp.text}")
    #     resp_json = resp.json()
    #     if resp.status_code != 200:
    #         print(resp_json)
    #         continue

    # from scrappers.cars.autoloancentre import AutoLoanCentreScrapper
    # scrapper = AutoLoanCentreScrapper()
    # scrapper.send_rest()

    # from scrappers.weedmaps.api.api_weedmaps import WeedmapsAPIScrapper
    # scrapper = WeedmapsAPIScrapper()
    # scrapper.get_data_from_api()
    # print(len(scrapper.api_collected))

    # from scrappers.gmaps import GmapsApiScrapper
    # scrapper = GmapsApiScrapper("dispensary", "Canada")
    # scrapper.start_scrapping()

    # base = "https://carnance-photos.s3.amazonaws.com/{}"
    # s3 = boto3.resource(
    #     "s3",
    #     aws_access_key_id="AKIAZMEE227CTW62T4MC",
    #     aws_secret_access_key="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",
    # )
    # bucket_name = "carnance-photos"
    # status_mapper = {
    #     "private": "sold",
    #     "draft": "new",
    #     "publish": "active",
    # }
    # with open("from_dima_car_to_vin (2).csv", "r") as reader_file:
    #     reader = csv.DictReader(reader_file, delimiter=";")
    #     for line in reader:
    #         vin = line["VIN"]
    #         idx = line["ID"]
    #         gallery = line["GALLERY_ID"]
    #         status = line["STATUS"]
    #
    #         print(f"{vin} GALLERY {gallery}")
    #         if gallery == '0':
    #             print(f"{vin} SKIPPED DUE EMPTY GALLERY")
    #             continue
    #
    #         car = CarProduct.query.filter(
    #             and_(CarProduct.vin == vin,
    #                  CarProduct.project == "carnance")
    #         ).first()
    #         if not car:
    #             print(f"{vin} SKIPPED DUE TO NO CAR WAS FOUND")
    #             continue
    #
    #         # uploaded = False
    #         # for image in car.images:
    #         #     if "carnance-photos.s3" in image:
    #         #         print(f"{vin} SKIPPED DUE TO ALREADY UPLOADED")
    #         #         uploaded = True
    #         #         break
    #         # if uploaded:
    #         #     continue
    #
    #         data = {
    #             "token": "zttLmtaGF8GnRHaq",
    #             "ID": idx,
    #             "galleryIDs": gallery,
    #         }
    #         headers = {"Content-type": "application/json"}
    #         print(f"{vin} DOWNLOADING")
    #         resp = requests.post(
    #             f"https://carnance.com/wp-json/car-gallery/v1/media/{idx}",
    #             json=data,
    #             headers=headers,
    #         )
    #         images = json.loads(resp.text)["imageUrl"]
    #
    #         new_images = []
    #         print(f"{vin} UPLOADING")
    #         total = len(images)
    #         passed = 0
    #         for image in images:
    #             if not isinstance(image, str):
    #                 continue
    #
    #             url = image.rstrip("/")
    #             ext = url.rsplit(".", 1)[1]
    #             filename = f"{uuid.uuid1()}.{ext}"
    #
    #             req_for_image = requests.get(url, stream=True)
    #
    #             file_object_from_req = req_for_image.raw
    #             req_data = file_object_from_req.read()
    #
    #             obj = s3.Bucket(bucket_name).put_object(
    #                 Key=f"{vin.lower()}/{filename}", Body=req_data
    #             )
    #             obj_path = base.format(obj.key)
    #             new_images.append(obj_path)
    #             # for my_bucket_object in my_bucket.objects.all():
    #             #     print(my_bucket_object)
    #             passed += 1
    #             print(f"{vin} {passed}/{total}")
    #
    #         car.status = status_mapper[status]
    #         car.images = new_images
    #         db.session.commit()
    #         print(f"{vin} OK")
