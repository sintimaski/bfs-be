import json
from typing import Dict

import cloudscraper
from bs4 import BeautifulSoup

from core.models import ThirdParty
from scrappers.cars.common.base_scrapper import BaseCarScrapper
from scrappers.cars.common.helpers import get_element_text
from scrappers.cars.getautofinance.common import get_from_json


class RexdaleHyundaiScrapper(BaseCarScrapper):
    def __init__(self, project):
        source = "rexdalehyundai"
        source_id = "43385"
        tp = ThirdParty.query.filter(
            ThirdParty.name == "carnance_vinaudit"
        ).first()
        api_key = tp.api_key
        super().__init__(
            source=source,
            vinaudit_key=api_key,
            project=project,
            source_id=source_id,
        )

    def get_dealership_data(self, car_url) -> Dict:
        try:
            scraper = cloudscraper.create_scraper()
            resp = scraper.get(car_url)
            resp_text = str(resp.text)
            soup = BeautifulSoup(markup=resp.text, features="html.parser")

            json_text = resp_text.split("DDC.dataLayer['vehicles'] = ", 1)[1]
            json_text = json_text.split(
                "// This is populated in the widget.js", 1
            )[0]
            json_text = json_text.strip(";\n")
            json_text = json_text.strip("[").strip("]")
            json_text = json_text.replace("\n", "")
            json_text = json_text.replace("\\'", "'")
            json_text = json_text.replace('\\"', "'")
            json_text = json_text.encode("unicode_escape").decode()
            json_data = json.loads(json_text)

            product_name = get_element_text(
                soup, "#vehicle-title1-app-root .font-weight-bold"
            )
            details = get_element_text(soup, ".ws-dealernotes div.content")
            if not details:
                details = get_element_text(soup, "#vehicleOverview")

            images = []
            for image in json_data.get("images", []):
                images.append(image.get("uri", ""))

            airbags = 0
            options = []
            packages = json_data.get("packages", [])
            if packages:
                packages = packages[0]
                options_list = packages.get("includedOptionList", [])
                for option in options_list:
                    text_map = option.get("textMap", {})
                    description = text_map.get("description", "")
                    options.append(description)
                    if "airbag" in description.lower():
                        airbags += 1

            odometer = get_from_json(json_data, "odometer")
            odometer = int(odometer)

            lda = json_data.get("address", {})
            location_dealer = (
                f'{lda.get("address1", "")} '
                f'{lda.get("city", "")} '
                f'{lda.get("country", "")} '
            )
            location_dealer = " ".join(location_dealer.split())
            location_dealer.strip()

            doors = get_from_json(json_data, "doors")
            doors = doors.split(" ", 1)[0]
            doors = int(doors) if doors.isnumeric() else None

            car_data = {
                "source": self.source,
                "source_id": self.source_id,
                "product_name": product_name,
                "price": int(get_from_json(json_data, "askingPrice")),
                "images": images,
                "odometer": odometer,
                "exterior_color": get_from_json(json_data, "exteriorColor"),
                "interior_color": get_from_json(json_data, "interiorColor"),
                "stock_number": get_from_json(json_data, "stockNumber"),
                "vin": get_from_json(json_data, "vin").strip(),
                "options": options,
                "details": details,
                "web_url": car_url,
                "location_diller": location_dealer,
                "airbags": airbags,
                "condition": get_from_json(json_data, "newOrUsed"),
                "doors": doors,
            }
            return car_data
        except Exception as e:
            return {"failed": car_url}

    def get_cars_urls(self):
        base_url = "https://www.rexdalehyundai.ca"
        listing_url = (
            "https://www.rexdalehyundai.ca/apis/widget/"
            "INVENTORY_LISTING_DEFAULT_AUTO_NEW:"
            "inventory-data-bus1/getInventory?start={}&pageSize={}"
        )
        start = 0
        page_size = 35
        while True:
            scraper = cloudscraper.create_scraper()
            resp = scraper.get(
                listing_url.format(start, page_size), timeout=120
            )
            data = json.loads(resp.text)
            inventory = data["inventory"]
            if not inventory:
                break
            for item in inventory:
                self.cars_urls.append(f'{base_url}{item["link"]}')
            start += page_size
