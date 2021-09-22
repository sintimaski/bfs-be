import json
from concurrent.futures.thread import ThreadPoolExecutor
from datetime import datetime
from pprint import pprint
from typing import Dict

import cloudscraper
from sqlalchemy import and_

from app import app
from core.db_connector import db
from core.helpers.mailer import Mailer
from core.models import CarProduct
from scrappers.cars.common.helpers import (
    adjust_car_data,
    _convert_odometer,
    filter_value,
)
from core.helpers.mailer.templates.export_template import cars_export_stats


class BaseCarScrapper:
    def __init__(
        self,
        source,
        project,
        source_id=None,
        vinaudit_key=None,
        carsxe_key=None,
        force_carsxe=None,
        fuelapi_key=None,
        apis_keys: Dict = None,
        send_report=None,
    ):
        self.MAX_RETRIES_ON_CAR = 3
        self.failed_counter = {}

        self.source = source
        self.project = project
        self.source_id = source_id

        self.vinaudit_key = vinaudit_key
        self.carsxe_key = carsxe_key
        self.force_carsxe = force_carsxe
        self.fuelapi_key = fuelapi_key
        if apis_keys:
            self.vinaudit_key = apis_keys.get("vinaudit")
            self.carsxe_key = apis_keys.get("carsxe")
            self.force_carsxe = apis_keys.get("force_carsxe")
            self.fuelapi_key = apis_keys.get("fuelapi")

        self.cars_urls = []
        self.vins_retrieved = []

        self.total_new = 0
        self.total_active = 0
        self.total_sold = 0
        self.send_report = send_report

    def start_scrapping(self):
        if not self._get_cars_urls():
            return
        self.get_cars_data()
        self.update_sold()

    def _get_cars_urls(self):
        max_retries = 5
        while max_retries > 0:
            try:
                self.get_cars_urls()
                return True
            except KeyboardInterrupt:
                return False
            except:
                max_retries -= 1
        return False

    def get_cars_urls(self):
        raise NotImplementedError

    def update_sold(self):
        vins_retrieved = [str(vin).upper() for vin in self.vins_retrieved]
        print(self.vins_retrieved, vins_retrieved)
        with app.app_context():
            missing = CarProduct.query.filter(
                and_(
                    CarProduct.vin.notin_(vins_retrieved),
                    CarProduct.source == self.source,
                )
            ).all()
            for missing_car in missing:
                if missing_car.status != "sold":
                    self.total_sold += 1
                missing_car.status = "sold"
            db.session.commit()

    def get_cars_data(self):
        failed = []
        succeed = 0
        passed = 0
        total = len(self.cars_urls)

        vins = []
        entities = CarProduct.query.with_entities(CarProduct.vin).all()
        for entity in entities:
            vins.append(entity.vin)

        with ThreadPoolExecutor(max_workers=8) as executor:
            for car_data in executor.map(self.get_car_data, self.cars_urls):
                passed += 1
                if "out" in car_data:
                    continue

                car_data.update({"project": self.project})

                if "failed" not in car_data:

                    vin = car_data["vin"].strip()
                    source = car_data["source"]
                    car_data = {k: filter_value(v) for k, v in car_data.items()}
                    car_data = adjust_car_data(car_data)

                    if self.car_exists(vin, source):
                        car = CarProduct.query.filter(
                            and_(
                                CarProduct.vin == vin,
                                CarProduct.source == source,
                            )
                        ).first()

                        car_data.pop("images", None)
                        car_data.update({"status": "active"})

                        for key, value in car_data.items():
                            value = filter_value(value)
                            setattr(car, key, value)

                        self.total_active += 1
                    else:
                        self.total_new += 1
                        # noinspection PyArgumentList
                        car = CarProduct(**car_data)
                        db.session.add(car)
                    succeed += 1
                    print(f"{succeed}/{passed}/{total}")
                else:
                    failed_url = car_data.get("failed", "")
                    self.failed_counter.update({
                        failed_url: self.failed_counter.get(failed_url, 0) + 1
                    })
                    failed.append(failed_url)
                    print(f"{succeed}/{passed}/{total}")
                db.session.commit()
        self.cars_urls = failed
        if failed:
            self.get_cars_data()

    def get_car_data(self, car_url: str, force_apis=False):
        if self.failed_counter.get(car_url, 0) >= self.MAX_RETRIES_ON_CAR:
            return {"out": car_url}

        dealership_data = self.get_dealership_data(car_url)
        if "failed" in dealership_data:
            print("dealership failed")
            return {"failed": car_url}

        if "out" in dealership_data:
            print("dealership out")
            return {"out": car_url}

        car_data = dealership_data
        vin = dealership_data["vin"]
        source = dealership_data["source"]
        self.vins_retrieved.append(vin)

        if not self.car_exists(vin, source) or force_apis:

            if self.vinaudit_key:
                vin_audit_data = self.get_vin_audit_data(vin)
                if "failed" in vin_audit_data:
                    print("vinaudit failed")
                    return {"failed": car_url}
                if "out" in dealership_data:
                    print("vinaudit out")
                    return {"out": car_url}
                car_data.update(vin_audit_data)
            car_data.update({"status": "new"})

            if self.fuelapi_key:
                # today = datetime.today()
                # today_year = today.year
                # if (car_data.get("year") - today_year) in [0, 1]:
                #     images = self.get_images_from_api(
                #         car_data.get("make"),
                #         car_data.get("model"),
                #         car_data.get("year"),
                #         car_data.get("exterior_color"),
                #     )
                #     car_data.update({"images": images})
                pass

            if self.carsxe_key:
                today = datetime.today()
                today_year = today.year
                if self.force_carsxe or (
                    car_data.get("year")
                    and (car_data.get("year") - today_year) in [0, 1]
                ):
                    images = self.get_images_from_api(
                        car_data.get("make"),
                        car_data.get("model"),
                        car_data.get("year"),
                        car_data.get("exterior_color"),
                    )
                    car_data.update({"images": images})

        return car_data

    def get_dealership_data(self, car_url: str):
        raise NotImplementedError

    def get_vin_audit_data(self, vin: str):
        try:
            url = (
                "https://specifications.vinaudit.com/v3/specifications?"
                "format=json&key={}&vin={}"
                "&include=attributes,equipment,warranties,colors"
            )
            scraper = cloudscraper.create_scraper()
            resp = scraper.get(url.format(self.vinaudit_key, vin))
            resp_data = json.loads(resp.text)
            if not resp_data.get("success", None):
                return {"out": True}

            _input = resp_data.get("input", {})
            _attributes = resp_data.get("attributes", {})

            _equipments = resp_data.get("equipments", {})
            airbags = 0
            equipments = []
            for equipment in _equipments:
                name = equipment.get("name", "")
                if "airbag" in name.lower():
                    airbags += 1
                equipments.append(
                    {
                        "group": equipment.get("group", ""),
                        "name": name,
                    }
                )

            data_formatter = {
                "make": {"dbname": "make"},
                "model": {"dbname": "model"},
                "year": {"lambda": lambda x: int(x)},
                "type": {"dbname": "body_type"},
                "size": {"dbname": "body_style"},
                "transmission_type": {"dbname": "transmission"},
                "trim": {},
                "engine": {},
                "engine_size": {"lambda": lambda x: f"{x} L"},
                "engine_cylinders": {"lambda": lambda x: int(x)},
                "drivetrain": {"dbname": "driveline"},
                "doors": {"lambda": lambda x: int(x.split("-", 1)[0])},
                "standard_seating": {
                    "dbname": "passengers",
                    "lambda": lambda x: int(x),
                },
                "fuel_type": {"dbname": "fuel"},
                "city_mileage": {
                    "lambda": lambda x: _convert_odometer(x),
                    "dbname": "city_fuel",
                },
                "highway_mileage": {
                    "lambda": lambda x: _convert_odometer(x),
                    "dbname": "hwy_fuel",
                },
            }
            options = [e["name"] for e in _equipments]
            car_data = {
                "vin": _input.get("vin", vin),
                "airbags": airbags,
                "options": options,
            }
            for field, data in data_formatter.items():
                value = _attributes.get(field, None)
                if value:
                    _lambda = data.get("lambda", lambda x: x)
                    _field = data.get("dbname", field)
                    car_data.update({_field: _lambda(value)})
            return car_data
        except Exception as e:
            print(e)
            return {"failed": True}

    def get_images_from_api(self, make, model, year, color):
        link = (
            f"http://api.carsxe.com/images?key={self.carsxe_key}&make={make}&"
            f"model={model}&year={year}&color={color}&size=Large&format=json"
        )
        scrapper = cloudscraper.create_scraper()
        resp = scrapper.get(link, timeout=120)
        data = json.loads(resp.text)

        images = []
        _images = data.get("images")
        if not data.get("success"):
            print(resp.text)
        for image in _images:
            url = image.get("link")
            if url:
                images.append(url)
        images = images[:1]

        return images

    @staticmethod
    def car_exists(vin, source):
        with app.app_context():
            exists = (
                CarProduct.query.filter(
                    and_(CarProduct.vin == vin, CarProduct.source == source)
                ).first()
                is not None
            )
        return exists

    def get_cars_data_for_test(
        self,
        cars_urls: list = None,
        first_n=None,
        force_apis=False,
        print_data=True,
        save=False,
    ):
        if not cars_urls:
            self.get_cars_urls()
            if first_n:
                self.cars_urls = self.cars_urls[:first_n]
        else:
            self.cars_urls = cars_urls

        print(f"Total in {self.__class__.__name__}: {len(self.cars_urls)}")

        for car_url in self.cars_urls:
            print(car_url)
            car_data = self.get_car_data(car_url, force_apis)

            if "out" in car_data:
                print(f"OUT {car_data['out']}")
                continue
            if "failed" in car_data:
                print(f"FAILED {car_data['failed']}")
                continue

            car_data = {k: filter_value(v) for k, v in car_data.items()}
            car_data = adjust_car_data(car_data)

            car_data["status"] = (
                "active"
                if CarProduct.query.filter(
                    CarProduct.vin == car_data["vin"].upper()
                ).first()
                is not None
                else "new"
            )

            if print_data:
                pprint(car_data)

            vin = car_data["vin"]
            if save and not self.car_exists(vin, car_data['source']):
                car_data.update({"status": "new"})
                # noinspection PyArgumentList
                new_car = CarProduct(**car_data)
                db.session.add(new_car)
                db.session.commit()
                print(f"Saved {car_data['vin']}")
