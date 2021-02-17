import json
from typing import List, Dict

from cloudscraper import create_scraper

from core.helpers.mailer import Mailer
from core.helpers.mailer.templates.export_template import cars_export_stats
from core.models import CarProduct
from . import (
    EasthillVWScrapper,
    OrillaKiaScrapper,
    PlazaKiaScrapper,
    Hwy11RamScrapper,
    SubaruDealerScrapper,
    OrillaVWScrapper,
    BoltonikaScrapper,
    MountainMitsubishiScrapper,
    NewMarketHyundaiScrapper,
    CambridgeMitsubishiScrapper,
    OrilliaHyundaiScrapper,
    CollingwoodHyundaiScrapper,
)


class GetAutoFinance:
    def __init__(
        self,
        scrape=True,
        send=True,
        send_active=True,
        send_sold=True,
        send_report=True,
    ):
        self.scrape = scrape
        self.send = send
        self.send_active = send_active
        self.send_sold = send_sold

        self.project = "getautofinance"

        self.scrappers = {
            EasthillVWScrapper,
            OrillaKiaScrapper,
            PlazaKiaScrapper,
            Hwy11RamScrapper,
            SubaruDealerScrapper,
            OrillaVWScrapper,
            BoltonikaScrapper,
            MountainMitsubishiScrapper,
            NewMarketHyundaiScrapper,
            CambridgeMitsubishiScrapper,
            OrilliaHyundaiScrapper,
            CollingwoodHyundaiScrapper,
        }
        self.dealerships = []
        for scrapper_class in self.scrappers:
            scrapper = scrapper_class(self.project)
            self.dealerships.append(scrapper.source)

        self.dev_token = "t6u3dJ3D6AY5eu5R5Rix"
        self.token = "Kek3zxaKvzeFnfoPLxzd"
        self.post_car_url = (
            "https://getautofinance.ca/wp-json/jwa-cars-listing/v1/cars/{}"
        )
        self.statuses_url = "https://getautofinance.ca/wp-json/jwa-cars-listing/v1/cars-status-import/"

        self.send_report = send_report
        self.total_active = 0
        self.total_new = 0
        self.total_sold = 0

    def start_routine(self):
        if self.scrape:
            self.start_scrapping()
        if self.send:
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
            scrapper = scrapper_class(self.project)
            scrapper.start_scrapping()

            self.total_active += scrapper.total_active
            self.total_new += scrapper.total_new
            self.total_sold += scrapper.total_sold

            print(f"Done {scrapper_class.__name__}")

    def update_rest(self):
        upload_to = "prod"
        vin_links = {
            "dev": "https://thompson.justwebagency.com/get-auto/wp-json/jwa-cars-listing/v1/cars-by-vin/{}",
            "prod": "https://getautofinance.ca/wp-json/jwa-cars-listing/v1/cars-by-vin/{}",
        }
        vin_link = vin_links[upload_to]
        update_inks = {
            "dev": "https://thompson.justwebagency.com/get-auto/wp-json/jwa-cars-listing/v1/cars/{}",
            "prod": "https://getautofinance.ca/wp-json/jwa-cars-listing/v1/cars/{}",
        }
        update_link = update_inks[upload_to]

        formatted = self.get_formatted_cars()
        status_mapper = {
            "sold": "private",
            "new": "draft",
            "active": "publish",
        }
        scrapper = create_scraper()
        passed = 0
        for car_data in formatted:
            car_data["carStatus"] = status_mapper[car_data["carStatus"]]
            car_data.update({"token": self.token})
            if not car_data.get("vin"):
                continue

            car_id = car_data["car_id"]
            if not car_id or upload_to == "dev":
                resp = scrapper.get(vin_link.format(car_data["vin"]))
                data = json.loads(resp.text)
                car_id = data.get("ID")

            if not car_id:
                continue

            _car_data = {
                "ID": car_id,
                "token": self.token,
                "status": "publish",
                "bodyType": car_data["bodyType"],
            }

            headers = {"Content-type": "application/json"}
            resp = scrapper.post(
                update_link.format(car_id),
                json=_car_data,
                headers=headers,
            )
            passed += 1
            print(resp.text)
            print(f"{passed}/{len(formatted)} {json.loads(resp.text)['ID']}")

    def send_rest(self):
        formatted = self.get_formatted_cars()
        scrapper = create_scraper()
        passed = 0
        status_mapper = {
            "sold": "private",
            "new": "draft",
            "active": "publish",
        }
        for car_data in formatted:
            car_data["carStatus"] = status_mapper[car_data["carStatus"]]

            car_data.update({"token": self.token})

            vin = car_data["vin"]
            resp = scrapper.get(
                "https://getautofinance.ca/wp-json/jwa-cars-listing/v1/cars-by-vin/{}".format(
                    vin
                )
            )

            print(resp.text)
            data = json.loads(resp.text)
            car_id = ""
            if data.get("statusCode") and data["statusCode"] == 200:
                car_id = data["ID"]
                car_data.update({"ID": car_id})
                car_data.pop("gallery", None)

            headers = {"Content-type": "application/json"}
            resp = scrapper.post(
                self.post_car_url.format(car_id), json=car_data, headers=headers
            )

            passed += 1
            print(f"{passed}/{len(formatted)} {resp.text}")

            resp_json = resp.json()

            if resp.status_code != 200:
                print(resp_json)
                continue

    def get_formatted_cars(self, with_car_id=True, vin=None) -> List[Dict]:
        cars_q = CarProduct.query.filter(
            CarProduct.source.in_(self.dealerships)
        )
        if not with_car_id:
            cars_q = cars_q.filter(CarProduct.car_id.is_(None))

        if vin:
            cars_q = cars_q.filter(CarProduct.vin == vin)

        cars = cars_q.all()
        formatted = []

        for car in cars:

            # if not self.send_active and car.status == "active":
            #     print('active')
            #     continue

            if not self.send_sold and car.status == "sold":
                continue

            if not car.make:
                continue
            if not car.price:
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

            car_data = {
                "id": car.id,
                # "source_id": car.source_id,
                "car_id": car.car_id,
                # "location_diller": car.location_diller,
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
                "carMileage": car.odometer or 0,
                # "condition": car.condition,
                # "driveline": driveline,
                "exteriorColor": car.exterior_color,
                "interiorColor": car.interior_color,
                "carEngine": car.engine or "",
                # "engine_size": car.engine_size,
                # "engine_cylinders": car.engine_cylinders,
                "price": [{"regular": int(car.price)}],
                "gallery": [img for img in car.images if "/thumb-" not in img],
                "transmission": transmission,
                # "options": "|".join(car.options or []),
                "carStatus": car.status,
                "dealer": [
                    {"address": car.location_diller},
                    {"dealerName": car.source},
                ],
            }

            self.get_int(car_data, "seatingNum", "passengers", car)
            # self.get_int(car_data, "carMileage", "odometer", car)
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
