import csv
import ftplib
import json
import uuid

import boto3
import requests
from sqlalchemy import and_
from datetime import datetime
from typing import List, Dict

import os
from cloudscraper import create_scraper

from core.db_connector import db
from core.helpers.mailer import Mailer
from core.helpers.mailer.templates.export_template import cars_export_stats
from core.models import CarProduct
from . import (
    DPAutoGroupScrapper,
    OntarioHyundaiCarsScrapper,
    RexdaleHyundaiScrapper,
    LuckyMotorCarsScrapper,
    BrothersDealsScrapper,
)


class CarnanceScrapper:
    def __init__(
        self,
        scrape=True,
        file_export=True,
        file_send=True,
        rest_send=True,
        send_report=True,
    ):
        self.scrape = scrape
        self.file_export = file_export
        self.file_send = file_send

        self.project = "carnance"

        self.scrappers = [
            DPAutoGroupScrapper,
            LuckyMotorCarsScrapper,
            BrothersDealsScrapper,
            OntarioHyundaiCarsScrapper,
            RexdaleHyundaiScrapper,
        ]
        self.dealerships = []
        for scrapper_class in self.scrappers:
            scrapper = scrapper_class(self.project)
            self.dealerships.append(scrapper.source)

        dir_path = os.path.dirname(os.path.realpath(__file__))
        self.filename = "cars.csv"
        self.filepath = os.path.join(dir_path, self.filename)

        self.rest_send = rest_send
        self.token = "MOevCNXZ6y121SlPjwAf"
        self.post_car_url = "https://carnance.com/wp-json/jwa-cars-listing/v1/cars/{}"
        self.vin_car_url = "https://carnance.com/wp-json/jwa-cars-listing/v1/cars-by-vin/{}"
        self.statuses_url = "https://carnance.com/wp-json/jwa-cars-listing/v1/cars-status-import/"

        self.send_report = send_report
        self.total_active = 0
        self.total_new = 0
        self.total_sold = 0

    def start_routine(self):
        if self.scrape:
            self.start_scrapping()
        if self.rest_send:
            self.send_rest()
        if self.send_report:
            self.report_send()

    def report_send(self):
        scrapper = create_scraper()
        resp = scrapper.get(self.statuses_url)
        data = json.loads(resp.text)

        mailer = Mailer()
        mailer.send_mail(
            project=str(self.project).capitalize(),
            text_message=cars_export_stats(
                total=data["all_car"],
                new=self.total_new,
                sold=self.total_sold,
                publish=data["publish"],
                draft=data["draft"],
                private=data["privat"],
            ),
            subject="Daily Report",
        )

    def start_scrapping(self):
        for scrapper_class in self.scrappers:
            print(f"Start {scrapper_class.__name__}")
            scrapper = scrapper_class(self.project)
            self.dealerships.append(scrapper.source)
            scrapper.start_scrapping()

            self.total_active += scrapper.total_active
            self.total_new += scrapper.total_new
            self.total_sold += scrapper.total_sold

            print(f"Done {scrapper_class.__name__}")

    def send_rest(self):
        formatted = self.get_formatted_cars()
        scrapper = create_scraper()

        passed = 0
        for car_data in formatted:
            car_data.pop("id", None)
            car_data.pop("car_id", None)
            car_data.update({"carStatus": 'draft'})

            if not car_data['vin'] or not car_data['price']:
                continue

            car_data.update({"token": self.token})

            vin = car_data["vin"]
            resp = scrapper.get(self.vin_car_url.format(vin))

            print(vin, resp.text)
            data = json.loads(resp.text)
            car_id = ""
            if data["statusCode"] == 200:
                car_id = data["ID"]
                car_data.update({"ID": car_id})
                car_data.update({"carStatus": data["carStatus"]})
                car_data.pop("gallery", None)
                if car_data["carStatus"] != "publish":
                    car_data.pop("gallery", None)
                elif not car_data.get('gallery'):
                    car_data.update({"carStatus": 'draft'})


            headers = {"Content-type": "application/json"}
            resp = scrapper.post(
                self.post_car_url.format(car_id), json=car_data, headers=headers
            )

            passed += 1
            print(f"    {passed}/{len(formatted)} {resp.text}")

            resp_json = resp.json()

            if resp.status_code != 200:
                print(resp_json)
                continue

    def get_formatted_cars(self) -> List[Dict]:
        cars = CarProduct.query.filter(
            and_(
                CarProduct.source.in_(self.dealerships),
                CarProduct.status.in_(["new", "sold"]),
            )
        ).all()
        formatted = []

        for car in cars:

            if not car.make:
                continue
            if not car.price or car.price == 0:
                continue

            today = datetime.today()
            today_year = today.year

            if not car.year or int(car.year) < (today_year - 6):
                continue

            if car.source in ["ontariohyundaicars", "rexdalehyundai"] and (
                int(car.year) - today_year
            ) not in [0, 1]:
                continue
            if car.source == "rexdalehyundai" and car.condition != "new":
                continue

            for image in car.images:
                if image.startswith("https://www.kbb.com"):
                    continue

            fuel = car.fuel or "Gas"
            fuel = fuel.lower()

            if fuel not in ["diesel", "electric"]:
                fuel = "Gas"
            else:
                fuel = car.fuel

            if car.body_type == "Sport Utility Vehicle":
                body_type = "SUV"
            else:
                body_type = car.body_type

            if car.transmission == "CVT":
                transmission = "Automatic"
            else:
                transmission = car.transmission

            driveline_mapper = {
                "Four-Wheel Drive": "AWD",
                "Front-Wheel Drive": "FWD",
                "All-Wheel Drive": "AWD",
                "Rear-Wheel Drive": "RWD",
                "Quattro": "AWD",
            }
            driveline = driveline_mapper.get(car.driveline, car.driveline)

            car_mileage = car.odometer or 0
            if int(car_mileage) < 100 and today_year - int(car.year) in [0, 1]:
                car_mileage = 0

            car_data = {
                "id": car.id,
                "car_id": car.car_id,
                "title": car.make,
                "vin": car.vin,
                "carStockNumber": car.stock_number,
                "cityMpg": car.city_fuel or "",
                "highwayMpg": car.hwy_fuel or "",
                "carMark": car.make,
                "carModel": car.model,
                "carTrim": f"{car.trim or ''} {car.engine or ''} {car.driveline or ''}".strip(),
                "carYear": car.year or 0,
                "bodyType": body_type or "",
                "fuelType": fuel,
                "carMileage": car_mileage,
                "exteriorColor": self.filter_symbols(car.exterior_color),
                "interiorColor": self.filter_symbols(car.interior_color),
                "carEngine": car.engine or "",
                "price": [{"regular": int(car.price)}],
                "gallery": [img for img in car.images if "/thumb-" not in img],
                "transmission": transmission or "",
                "carStatus": car.status,
                "drivetrain": driveline,
                "features": "|".join(car.options),
                "dealer": [
                    {"address": car.location_diller},
                    {"dealerName": car.source},
                ],
            }

            self.get_int(car_data, "seatingNum", "passengers", car)
            self.get_int(car_data, "airbagNum", "airbags", car)
            self.get_int(car_data, "doorsNum", "doors", car)

            formatted.append(car_data)

        print(f"CARS TOTAL: {len(formatted)}")
        return formatted

    def get_int(self, car_data, name, name_model, car):
        model_value = getattr(car, name_model)
        _value = int(model_value) if str(model_value).isnumeric() else None
        if _value:
            car_data.update(
                {
                    name: _value,
                }
            )

    @staticmethod
    def upload_to_s3():
        base = "https://carnance-photos.s3.amazonaws.com/{}"
        s3 = boto3.resource(
            "s3",
            aws_access_key_id="AKIAZMEE227CTW62T4MC",
            aws_secret_access_key="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",
        )
        bucket_name = "carnance-photos"
        with open("../../../car_vin_gallery.csv", "r") as reader_file:
            reader = csv.DictReader(reader_file)
            for line in reader:
                vin = line["VIN"]
                idx = line["ID"]
                gallery = line["GALLERY_ID"]
                print(f"{vin} GALLERY {gallery}")
                if gallery == "0":
                    print(f"{vin} SKIPPED DUE EMPTY GALLERY")
                    continue

                data = {
                    "token": "zttLmtaGF8GnRHaq",
                    "ID": idx,
                    "galleryIDs": gallery,
                }
                headers = {"Content-type": "application/json"}
                print(f"{vin} DOWNLOADING")
                resp = requests.post(
                    f"https://carnance.com/wp-json/car-gallery/v1/media/{idx}",
                    json=data,
                    headers=headers,
                )
                images = json.loads(resp.text)["imageUrl"]

                new_images = []
                print(f"{vin} UPLOADING")
                total = len(images)
                passed = 0
                for image in images:
                    if not isinstance(image, str):
                        continue

                    url = image.rstrip("/")
                    ext = url.rsplit(".", 1)[1]
                    filename = f"{uuid.uuid1()}.{ext}"

                    req_for_image = requests.get(url, stream=True)

                    file_object_from_req = req_for_image.raw
                    req_data = file_object_from_req.read()

                    obj = s3.Bucket(bucket_name).put_object(
                        Key=f"{vin.lower()}/{filename}", Body=req_data
                    )
                    obj_path = base.format(obj.key)
                    new_images.append(obj_path)
                    # for my_bucket_object in my_bucket.objects.all():
                    #     print(my_bucket_object)
                    passed += 1
                    print(f"{vin} {passed}/{total}")
                car = CarProduct.query.filter(
                    and_(
                        CarProduct.vin == vin, CarProduct.project == "carnance"
                    )
                ).first()
                if car:
                    car.images = new_images
                    db.session.commit()
                print(f"{vin} OK")

    @staticmethod
    def filter_symbols(string):
        if string is None:
            return ""
        filter_chars = [
            '"',
            "!",
            "@",
            "#",
            "$",
            "%",
            "^",
            "&",
            "*",
            "(",
            ")",
            "_",
            "+",
            "{",
            "}",
            "|",
            ":",
            '"',
            "<",
            ">",
            "?",
            "[",
            "]",
            ";",
            "'",
            ",",
            ".",
            "/",
            "~",
            "`",
            "=",
        ]
        return "".join([c for c in string if c not in filter_chars])
