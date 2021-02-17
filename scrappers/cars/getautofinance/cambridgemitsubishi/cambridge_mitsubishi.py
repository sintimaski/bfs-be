from typing import Dict

import cloudscraper
from bs4 import BeautifulSoup

from scrappers.cars.getautofinance.common import PlazaLikeScrapper, get_element_text


class CambridgeMitsubishiScrapper(PlazaLikeScrapper):
    def __init__(self, project):
        source = "cambridge-mitsubishi"
        super().__init__(source, project)

    @staticmethod
    def get_from_next_sibling(soup, text):
        tag_prev = soup.find("div", string=text)
        value = tag_prev.findNext("div").text if tag_prev else ""
        value = value.strip()
        value = "" if value == "N/A" else value
        return value

    def get_dealership_data(self, car_url) -> Dict:
        try:
            scraper = cloudscraper.create_scraper()
            resp = scraper.get(car_url)
            soup = BeautifulSoup(markup=resp.text, features="html.parser")

            out = soup.select_one('img[src="/images/410.png"]')
            if out:
                return {"out": car_url}

            _images = soup.select("ul#imageGallery li img")
            images = []
            for _image in _images:
                src = _image.get("src")
                if src:
                    images.append(src)

            year = self.get_from_next_sibling(soup, " Year ")
            year = int(year) if year else None

            doors = self.get_from_next_sibling(soup, " Doors ")
            doors = int(doors) if doors else None

            passengers = self.get_from_next_sibling(soup, " Passenger ")
            passengers = int(passengers) if passengers else None

            stock = soup.select_one(".stock-num")
            stock.select_one("span").extract()
            stock_number = stock.text

            price = soup.select_one(".our-price-div .primary")
            price = price.text if price else ""
            price = "".join([p for p in price if p.isnumeric()])
            price = int(price) if price else None

            make = self.get_from_next_sibling(soup, " Make ")
            model = self.get_from_next_sibling(soup, " Model ")
            trim = self.get_from_next_sibling(soup, " Trim ")
            transmission = self.get_from_next_sibling(soup, " Transmission ")
            engine = self.get_from_next_sibling(soup, " Engine Size ")
            vin = self.get_from_next_sibling(soup, " Vin ")
            exterior_color = self.get_from_next_sibling(
                soup, " Exterior Color "
            )
            interior_color = self.get_from_next_sibling(soup, " Color ")
            product_name = get_element_text(soup, ".model-title")
            details = get_element_text(soup, ".ShowReadMore")
            body_type = self.get_from_next_sibling(soup, " Body Style ")
            fuel = self.get_from_next_sibling(soup, " Fuel Type ")

            condition = self.get_from_next_sibling(soup, " Sale Type ")
            condition = condition.lower() or "used"

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
                "body_type": body_type,
                "doors": doors,
                "condition": condition,
                "transmission": transmission,
                "passengers": passengers,
                "exterior_color": exterior_color,
                "interior_color": interior_color,
                "fuel": fuel,
                "stock_number": stock_number,
                "vin": vin,
                "details": details,
                "web_url": car_url,
            }
            return car_data
        except Exception as e:
            return {"failed": car_url}

    def get_cars_urls(self):
        base_url = "http://cambridge-mitsubishi.com"
        listing_url = (
            "https://cambridge-mitsubishi.ca/Used-Inventory/?filters[limit]=10000"
        )
        scraper = cloudscraper.create_scraper()
        resp = scraper.get(listing_url, timeout=120)
        soup = BeautifulSoup(markup=resp.text, features="html.parser")
        tags = soup.select(".model-title-link.pushstate")
        for tag in tags:
            href = tag.get("href")
            if href:
                self.cars_urls.append(f"{base_url}{href}")

        listing_url = (
            "https://cambridge-mitsubishi.ca/In-Stock/?filters[limit]=10000"
        )
        scraper = cloudscraper.create_scraper()
        resp = scraper.get(listing_url, timeout=120)
        soup = BeautifulSoup(markup=resp.text, features="html.parser")
        tags = soup.select(".model-title-link.pushstate")
        for tag in tags:
            href = tag.get("href")
            if href:
                self.cars_urls.append(f"{base_url}{href}")
