import json
import traceback
from typing import Dict

import cloudscraper
from bs4 import BeautifulSoup

from scrappers.cars.common.base_scrapper import BaseCarScrapper


class PlazaLikeScrapper(BaseCarScrapper):
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
            city_fuel = get_from_json(json_data, "cityFuelEfficiency")
            city_fuel = f"{city_fuel}L/100Km"
            hwy_fuel = get_from_json(json_data, "highwayFuelEfficiency")
            hwy_fuel = f"{hwy_fuel}L/100Km"

            lda = json_data.get("address", {})
            location_diller = (
                f'{lda.get("address1", "")} '
                f'{lda.get("city", "")} '
                f'{lda.get("country", "")} '
            )
            location_diller = " ".join(location_diller.split())
            location_diller.strip()

            doors = get_from_json(json_data, "doors")
            doors = doors.split(" ", 1)[0]
            doors = int(doors) if doors.isnumeric() else None

            engine = ''
            sps = soup.select("#quick-specs1-app-root .text-muted")
            for sp in sps:
                if sp.text == 'Engine':
                    _sp = sp.next_sibling
                    engine = _sp.text if _sp else ''

            car_data = {
                "source": self.source,
                "product_name": product_name,
                "trim": get_from_json(json_data, "trim"),
                "condition": get_from_json(json_data, "newOrUsed"),
                "price": int(get_from_json(json_data, "askingPrice")),
                "images": images,
                "make": get_from_json(json_data, "make"),
                "model": get_from_json(json_data, "model"),
                "year": int(get_from_json(json_data, "modelYear")),
                "body_type": get_from_json(json_data, "bodyStyle"),
                "odometer": odometer,
                "transmission": get_from_json(json_data, "transmission"),
                "engine": engine,
                "engine_size": get_from_json(json_data, "engineSize"),
                "driveline": get_from_json(json_data, "driveline"),
                "exterior_color": get_from_json(json_data, "exteriorColor"),
                "interior_color": get_from_json(json_data, "interiorColor"),
                "doors": doors,
                "fuel": get_from_json(json_data, "fuelType"),
                "city_fuel": city_fuel,
                "hwy_fuel": hwy_fuel,
                "stock_number": get_from_json(json_data, "stockNumber"),
                "vin": get_from_json(json_data, "vin"),
                "details": details,
                "options": options,
                "web_url": car_url,
                "location_diller": location_diller,
                "airbags": airbags,
            }
            return car_data
        except Exception as e:
            print(traceback.format_exc())
            return {"failed": car_url}


def get_element_text(soup, selector) -> str:
    tag = soup.select_one(selector)
    text = tag.text if tag else ""
    if text == "null" or text is None:
        text = ""
    return text


def get_from_json(data, name) -> str:
    value = str(data.get(name, ""))
    value = value.encode().decode("unicode_escape")
    return value
