import json
import traceback
from datetime import datetime

import cloudscraper
from bs4 import BeautifulSoup

from core.models import ThirdParty
from scrappers.cars.common.base_scrapper import BaseCarScrapper
from scrappers.cars.common.helpers import get_element_text


def get_text_by_sibling(soup, span_text, sibling_tag="span") -> str:
    sibling = soup.find(
        lambda tag: tag.name == sibling_tag and span_text in tag.text
    )
    text = ""
    if sibling:
        parent = sibling.parent
        try:
            tag = parent.select("span")[1]
            text = tag.text if tag else ""
        finally:
            pass
    return text


class OntarioHyundaiCarsScrapper(BaseCarScrapper):
    def __init__(self, project):
        source = "ontariohyundaicars"
        source_id = "43406"
        tpva = ThirdParty.query.filter(
            ThirdParty.name == "carnance_vinaudit"
        ).first()
        vinaudit_key = tpva.api_key
        tpcx = ThirdParty.query.filter(
            ThirdParty.name == "carnance_carsxe"
        ).first()
        carsxe_key = tpcx.api_key
        super().__init__(
            source=source,
            vinaudit_key=vinaudit_key,
            carsxe_key=carsxe_key,
            project=project,
            source_id=source_id
        )

    def get_dealership_data(self, car_url: str):
        try:
            scraper = cloudscraper.create_scraper()
            resp = scraper.get(car_url)
            soup = BeautifulSoup(markup=resp.text, features="html.parser")

            product_name = get_element_text(soup, ".heading-year-make-model")

            price = soup.select_one("span#final-price")
            price = price.text if price else ""
            price = "".join([p for p in price if p.isdigit()])
            if price:
                price = int(price)

            images_tags = soup.select("ul#imgList img")
            images = []
            for image_tag in images_tags:
                images.append(image_tag.get("data-src", ""))

            options = []
            options_tags = soup.select(
                "tbody td.table-options-text.table-options-td"
            )
            for option in options_tags:
                print(option.text)
                options.append(option.text)

            odometer = soup.select_one("span.mileage-used-value")
            odometer = odometer.text if odometer else ""
            odometer = "".join([o for o in odometer if o.isdigit()]) or 0
            odometer = int(odometer)

            _exterior_color = soup.select_one('td[itemprop="color"]')
            exterior_color = _exterior_color.text if _exterior_color else ""

            _interior_color = soup.select_one(
                'td[itemprop="vehicleInteriorColor"]'
            )
            interior_color = _interior_color.text if _interior_color else ""

            _stock_number = soup.select_one('.col-used-value[itemprop="sku"]')
            stock_number = _stock_number.text if _stock_number else ""

            _vin = resp.text.split("&vin=", 1)[1]
            vin = _vin.split("&", 1)[0]

            details_tag = soup.select_one('span[itemprop="description"]')
            details = details_tag.text if details_tag else ""

            location_dealer_tag = soup.select_one(".seller-address")
            location_dealer = (
                location_dealer_tag.text if location_dealer_tag else ""
            )

            condition = soup.select_one('span[itemprop="itemCondition"]')
            condition = condition.text if condition else "used"
            condition = condition.lower()

            car_data = {
                "source": self.source,
                "source_id": self.source_id,
                "product_name": product_name,
                "price": price,
                "images": images,
                "odometer": odometer,
                "exterior_color": exterior_color,
                "interior_color": interior_color,
                "stock_number": stock_number,
                "vin": vin.strip(),
                "details": details,
                "web_url": car_url,
                "condition": condition,
                "location_diller": location_dealer,
            }
            return car_data
        except Exception as e:
            print(car_url)
            print(traceback.format_exc())
            return {"failed": car_url}

    def get_cars_urls(self):
        base_url = "https://www.ontariohyundaicars.com"
        link = "https://www.ontariohyundaicars.com/new/pg/{}"
        page = 1
        while True:
            scraper = cloudscraper.create_scraper()
            data = {
                "ajax": True,
                "refresh": True,
            }
            resp = scraper.post(link.format(page), data=data)
            data = json.loads(resp.text)

            vehicles = data.get("vehicles")
            for vehicle in vehicles:
                cell = vehicle.get("vehicleCellHTML")
                soup = BeautifulSoup(markup=cell, features="html.parser")
                item = soup.select_one("div.item.active a") or soup.select_one(
                    "div.image-grid-size a"
                )
                href = item.get("href")
                self.cars_urls.append(f"{base_url}{href}")
            page += 1
            if not vehicles:
                break
