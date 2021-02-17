import traceback
from typing import Dict

import cloudscraper
from bs4 import BeautifulSoup

from scrappers.cars.common.base_scrapper import BaseCarScrapper

from scrappers.cars.getautofinance.common import get_element_text
from scrappers.cars.common.helpers import find_between


class ApexMotorCarsScrapper(BaseCarScrapper):
    def __init__(self):
        self.cars_urls = []
        self.source = "apexmotorcars"
        self.source_id = "19445"
        super().__init__(self.source)

    def get_dealership_data(self, car_url: str) -> Dict:
        try:
            scraper = cloudscraper.create_scraper()
            resp = scraper.get(car_url)
            soup = BeautifulSoup(markup=resp.text, features="html.parser")
            images = []
            images_tags = soup.select("ul#imgList img")
            for tag in images_tags:
                src = tag.get("data-src", None)
                if src:
                    images.append(src)

            price = get_element_text(soup, 'span[itemprop="price"]')
            price = "".join(c for c in price if c.isdigit())
            product_name = get_element_text(
                soup, "h1.heading-year-make-model"
            )
            make = get_element_text(soup, 'span[itemprop="manufacturer"]')
            year = get_element_text(soup, 'span[itemprop="releaseDate"]')
            body_style = get_element_text(soup, 'td[itemprop="bodyType"]')
            odometer = get_element_text(soup, ".mileage-used-value")
            exterior_color = get_element_text(soup, 'td[itemprop="color"]')
            interior_color = get_element_text(
                soup, 'td[itemprop="vehicleInteriorColor"]'
            )
            driveline = get_element_text(
                soup, 'td[itemprop="driveWheelConfiguration"]'
            )
            transmission = get_element_text(
                soup, 'td[itemprop="vehicleTransmission"]'
            )
            stock_number = get_element_text(soup, 'td[itemprop="sku"]')
            fuel = get_element_text(soup, 'td[itemprop="fuelType"]')
            location_diller = get_element_text(
                soup, "#tr_city_details .col-used-value"
            )
            details = get_element_text(
                soup, 'span[itemprop="description"]'
            )

            # TODO add choice (new, active, sold) to car model.
            status = "active"
            if "***SOLD***" in details:
                status = "sold"

            engine_text = get_element_text(
                soup, 'td[itemprop="vehicleEngine"]'
            )
            try:
                engine_size = engine_text.split(" ", 1)[0]
            except IndexError:
                engine_size = ""
            try:
                engine = engine_text.split(" ", 1)[1]
            except IndexError:
                engine = ""

            _model = resp.text.split('model: "', 1)[1]
            model = _model.split('",', 1)[0]

            options = []
            page_text = str(soup)
            while True:
                option = find_between(
                    page_text,
                    '<td class="table-options-text table-options-td">',
                    "</td>",
                )
                if not option:
                    break
                page_text = page_text.replace(
                    "table-options-text table-options-td", "", 1
                )
                options.append(option)

            vin_tag = soup.select_one('input[name^="vin-"]')
            vin = (
                vin_tag.get("value", "").replace("vin-", "") if vin_tag else ""
            )
            vin = vin.lower()

            sold = soup.select_one("#redirect")
            if sold:
                status = "sold"
                return {
                    "source": self.source,
                    "source_id": self.source_id,
                    "vin": vin,
                    "status": status,
                }

            car_data = {
                "source": self.source,
                "source_id": self.source_id,
                "status": status,
                "product_name": product_name,
                "price": price,
                "images": images,
                "make": make,
                "model": model,
                "year": year,
                "body_style": body_style,
                "odometer": odometer,
                "transmission": transmission,
                "engine": engine,
                "engine_size": engine_size,
                "driveline": driveline,
                "exterior_color": exterior_color,
                "interior_color": interior_color,
                "fuel": fuel,
                "stock_number": stock_number,
                "vin": vin,
                "details": details,
                "options": options,
                "web_url": car_url,
                "location_diller": location_diller,
            }
            return car_data
        except Exception as e:
            print(car_url)
            # print(e)
            print(traceback.format_exc())
            return {"failed": car_url}

    def get_cars_urls(self):
        base_url = "http://vehicles.apexmotorcars.ca"
        listing_url = "http://vehicles.apexmotorcars.ca/used/pg/{}"
        page = 1
        while True:
            scraper = cloudscraper.create_scraper()
            resp = scraper.get(listing_url.format(page))
            soup = BeautifulSoup(markup=resp.text, features="html.parser")
            cars_urls_tags = soup.select(
                ".vehicle-year-make-model .stat-text-link"
            )
            if not cars_urls_tags:
                break
            for car_url_tag in cars_urls_tags:
                self.cars_urls.append(
                    f'{base_url}{car_url_tag.get("href", "")}'
                )

            page += 1
