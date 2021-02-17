import json
from typing import Dict

import cloudscraper
from bs4 import BeautifulSoup

from scrappers.cars.getautofinance.common import (
    PlazaLikeScrapper,
)


class CollingwoodHyundaiScrapper(PlazaLikeScrapper):
    def __init__(self, project):
        source = "collingwoodhyundai"
        super().__init__(source, project)

    def get_dealership_data(self, car_url) -> Dict:
        try:
            scraper = cloudscraper.create_scraper()
            resp = scraper.get(car_url)
            soup = BeautifulSoup(markup=resp.text, features="html.parser")

            product_name_tag = soup.select_one(".makeModelYear")
            product_name = product_name_tag.text

            vin_tag = soup.select_one("#carproofcarvin")
            vin = vin_tag.get("value")

            topcarid_tag = soup.select_one("#topcarid")
            topcarid = topcarid_tag.get("value")
            if not topcarid or not vin:
                return {"out": car_url}

            json_link = "https://www.collingwoodhyundai.com/js/json/{}.json"
            resp = scraper.get(json_link.format(topcarid))

            data = json.loads(resp.text)

            make = data.get("make")
            model = data.get("model")
            trim = data.get("version_en")

            year = data.get("year")
            year = int(year) if year else None

            price = data.get("price")
            price = int(price) if price else None

            odometer = data.get("miles")
            odometer = int(odometer) if odometer else None

            exterior_color = data.get("colorEN")
            interior_color = data.get("couleur_interieurEN")
            transmission = data.get("transmissionEN")
            engine = data.get("engineType")
            stock_number = data.get("no_stock")
            details = data.get("descriptionAn")
            city_fuel = f"{data.get('cityConsumption')}L/100Km"
            hwy_fuel = f"{data.get('highwayConsumption')}L/100Km"

            images = []
            photos = data.get('photos', [])
            for photo in photos:
                image_uri = photo.get('imageURI')
                if image_uri:
                    images.append(image_uri)

            car_data = {
                "source": self.source,
                "product_name": product_name,
                "trim": trim,
                "price": price,
                "images": images,
                "make": make,
                "model": model,
                "year": year,
                "engine": engine,
                "odometer": odometer,
                "transmission": transmission,
                "exterior_color": exterior_color,
                "interior_color": interior_color,
                "stock_number": stock_number,
                "vin": vin,
                "city_fuel": city_fuel,
                "hwy_fuel": hwy_fuel,
                "details": details,
                "web_url": car_url,
            }
            return car_data
        except Exception as e:
            return {"failed": car_url}

    def get_cars_urls(self):
        listing_url = "https://www.collingwoodhyundai.com/inventory.html?filterid=a8q{}-10"
        q = 0
        urls = []
        while True:
            scraper = cloudscraper.create_scraper()
            resp = scraper.get(listing_url.format(q), timeout=120)
            soup = BeautifulSoup(resp.text, features="html.parser")
            a_tags = soup.select("div.carImage > a")
            if not a_tags:
                break
            if a_tags[0].get("href").strip("/") == "{{url}}":
                continue

            for a_tag in a_tags:
                url = f'https://{a_tag.get("href").strip("/")}'
                urls.append(url)
            q += 1
        self.cars_urls = urls
        print(urls)
