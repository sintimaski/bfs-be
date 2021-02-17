import traceback
from typing import Dict

import cloudscraper
from bs4 import BeautifulSoup

from scrappers.cars.getautofinance.common import PlazaLikeScrapper


def get_tt(soup, selector):
    try:
        _elem = soup.select_one(selector)
        _elem_parent = _elem.parent
        elem = _elem_parent.select_one("span")
        text = elem.text or ""
        text = " ".join(text.split())
    except:
        return ""
    return text


class SprinterKingScrapper(PlazaLikeScrapper):
    def __init__(self, project):
        source = "sprinterking"
        super().__init__(source=source, project=project)

    def get_dealership_data(self, car_url) -> Dict:
        try:
            scraper = cloudscraper.create_scraper()
            resp = scraper.get(car_url)
            resp_text = str(resp.text)
            soup = BeautifulSoup(markup=resp.text, features="html.parser")

            _nfull = soup.select_one(
                ".inventory-name-price .inventory-name-inner h1"
            ).text.strip()
            _n = _nfull.split(" ")
            print(_n)

            year = _n[0]
            year = int(year)

            make = _n[1]
            model = _n[2]
            trim = " ".join(_n[3:])

            _p = soup.select_one(".inventory-price-inner h2")
            _p = _p.text if _p else ""
            _p = "".join([p for p in _p if p.isnumeric()]) or 0
            price = int(_p)

            _vin = soup.find("span", string="VIN #:")
            _vinp = _vin.parent
            _vin.extract()
            vin = _vinp.text if _vinp else ""

            _stock = soup.find("span", string="Stock #:")
            _stockp = _stock.parent
            _stock.extract()
            stock_number = _stockp.text if _stockp else ""

            odometer = get_tt(soup, '[title="Odometer"]')
            odometer = "".join([p for p in odometer if p.isnumeric()]) or 0

            exterior_color = get_tt(soup, '[title="Exterior Color"]')
            interior_color = get_tt(soup, '[title="Interior Color"]')
            body_type = get_tt(soup, '[title="Body Type"]')
            fuel = get_tt(soup, '[title="Fuel Type"]')
            transmission = get_tt(soup, '[title="Transmission"]')
            driveline = get_tt(soup, '[title="Drive Train"]')
            engine = get_tt(soup, '[title="Engine Data"]')

            images = []
            _images = soup.select('.carousel-inner .item img')
            for image in _images:
                src = image.get('src')
                if src:
                    images.append(f"https://www.sprinterking.ca/{src}")

            car_data = {
                "source": self.source,
                "product_name": _nfull,
                "trim": trim,
                "price": price,
                "images": images,
                "make": make,
                "model": model,
                "year": year,
                "body_type": body_type,
                "odometer": odometer,
                "transmission": transmission,
                "engine": engine,
                "driveline": driveline,
                "exterior_color": exterior_color,
                "interior_color": interior_color,
                "fuel": fuel,
                "stock_number": stock_number,
                "vin": vin,
                "web_url": car_url,
            }
            return car_data
        except Exception as e:
            print(traceback.format_exc())
            return {"failed": car_url}

    def get_cars_urls(self):
        base_url = "https://www.sprinterking.ca"
        listing_url = (
            "https://www.sprinterking.ca/inventory?page={}&per-page={}"
        )
        page = 1
        ppage = 12
        while True:
            scraper = cloudscraper.create_scraper()
            resp = scraper.get(listing_url.format(page, ppage), timeout=120)

            soup = BeautifulSoup(markup=resp.text, features="html.parser")
            vehicles = soup.select(".listing-vechile-one")
            for vehicle in vehicles:
                sold = vehicle.select_one("span.sold")
                if sold:
                    continue

                atag = vehicle.select_one(".eziVehicleName a")
                if atag:
                    href = atag.get("href")
                    if href:
                        self.cars_urls.append(f"{base_url}{href}")

            next = soup.select_one(".next:not(.disabled) a")
            if next:
                page += 1
                continue
            return
