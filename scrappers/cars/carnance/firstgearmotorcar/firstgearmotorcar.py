from typing import Dict

import cloudscraper
from bs4 import BeautifulSoup

from scrappers.cars.common.base_scrapper import BaseCarScrapper
from ..helpers import get_text_by_sibling_text


def text_by_sibl_img_slctr(soup, img_selector) -> str:
    img = soup.select_one(img_selector)
    if img:
        parent = img.parent
        span = parent.select_one("span")
        text = span.text if span else ""
        text = text.replace("\n", "")
        text = " ".join(text.split())
        return text
    return ""


class FirstGearMotorCarScrapper(BaseCarScrapper):
    def __init__(self, project):
        self.makes = []
        self.cars_urls = []
        source = "firstgearmotorcar"
        self.source = source
        self.source_id = "19441"
        # super.__init__(source=source, project=project)

    def start_scrapping(self):
        self.get_cars_urls()
        self.check_for_out_stock()
        self.get_makes()
        self.get_cars_data()

    def get_makes(self):
        listing_url = "https://www.firstgearmotorcar.com/vehicles"
        scraper = cloudscraper.create_scraper()
        resp = scraper.get(listing_url)
        soup = BeautifulSoup(markup=resp.text, features="html.parser")
        tags = soup.select('.eziFilterMake div[qsname="Makes"] a.lnk')
        for tag in tags:
            text = tag.text
            self.makes.append(text.lower())

    def get_dealership_data(self, car_url) -> Dict:
        try:
            scraper = cloudscraper.create_scraper()
            resp = scraper.get(car_url)
            soup = BeautifulSoup(markup=resp.text, features="html.parser")

            product_name = self.get_element_text(
                soup, "div.inventory-name-inner h1"
            )
            product_name = product_name.lower()

            make = ""
            product_name_lower = product_name.lower()
            for _make in self.makes:
                if _make in product_name_lower:
                    make = _make
                    break

            _model = car_url.rsplit("/", 1)[0]
            _model = _model.rsplit("/", 1)[1]
            _model = _model.split(make.lower().replace(" ", "-"), 1)[1]
            model = _model.replace("-", " ").strip()

            year = product_name.split(" ", 1)[0]
            price = self.get_element_text(soup, "div.inventory-price-inner h2")
            price = "".join(c for c in price if c.isdigit())

            vin = get_text_by_sibling_text(soup, "VIN #:")
            vin = vin.lower()

            stock_number = get_text_by_sibling_text(soup, "Stock #:")
            stock_number = stock_number.lower()

            odometer = text_by_sibl_img_slctr(soup, 'img[title="Odometer"]')
            exterior_color = text_by_sibl_img_slctr(
                soup, 'img[title="Exterior Color"]'
            )
            interior_color = text_by_sibl_img_slctr(
                soup, 'img[title="Interior Color"]'
            )
            body_style = text_by_sibl_img_slctr(soup, 'img[title="Body Type"]')
            driveline = text_by_sibl_img_slctr(soup, 'img[title="Drive Train"]')
            transmission = text_by_sibl_img_slctr(
                soup, 'img[title="Transmission"]'
            )
            fuel = text_by_sibl_img_slctr(soup, 'img[title="Fuel Type"]')

            engine_data = text_by_sibl_img_slctr(
                soup, 'img[title="Engine Data"]'
            )
            engine = ""
            engine_size = ""
            if engine_data:
                engine_data = engine_data.split(" Engine ")
                try:
                    engine = engine_data[0]
                    engine_size = engine_data[1]
                except IndexError:
                    pass

            fuel_economy = text_by_sibl_img_slctr(
                soup, 'img[title="Fuel Economy"]'
            )
            city_fuel = ""
            hwy_fuel = ""
            if fuel_economy:
                fuel_economy = fuel_economy.split(" / ")
                try:
                    city_fuel = f"{fuel_economy[0].split(' ')[0]}L/100Km"
                    hwy_fuel = f"{fuel_economy[1].split(' ')[0]}L/100Km"
                except IndexError:
                    pass

            images = []
            images_tags = soup.select("img.banner-img")
            for tag in images_tags:
                src = tag.get("src", None)
                if src:
                    base_url = "https://www.firstgearmotorcar.com"
                    images.append(f"{base_url}{src}")

            location_diller_tag = soup.select_one("#dealershipLocation")
            location_diller = (
                location_diller_tag.text if location_diller_tag else ""
            )

            options = []
            options_tags = soup.select("div.features li")
            for tag in options_tags:
                options.append(tag.text)

            details_header = soup.select_one(".vehicle-overview h6")
            if details_header:
                details_header.extract()
            details_tag = soup.select_one(".vehicle-overview")
            details = details_tag.text if details_tag else ""

            car_data = {
                "source": self.source,
                "source_id": self.source_id,
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
                "city_fuel": city_fuel,
                "hwy_fuel": hwy_fuel,
                "stock_number": stock_number,
                "vin": vin,
                "details": details,
                "options": options,
                "web_url": car_url,
                "location_diller": location_diller,
            }
            return car_data
        except Exception as e:
            return {"failed": car_url}

    def get_cars_urls(self):
        base_url = "https://www.firstgearmotorcar.com"
        listing_url = (
            "https://www.firstgearmotorcar.com/vehicles?page={}&per-page=12"
        )
        page = 1
        while True:
            scraper = cloudscraper.create_scraper()
            resp = scraper.get(listing_url.format(page))
            soup = BeautifulSoup(markup=resp.text, features="html.parser")
            cars_urls_tags = soup.select("h2.eziVehicleName a")
            if not cars_urls_tags:
                break
            for car_url_tag in cars_urls_tags:
                self.cars_urls.append(
                    f'{base_url}{car_url_tag.get("href", "")}'
                )
            next_disabled = soup.select_one("ul.pagination li.next.disabled")
            if next_disabled:
                break
            page += 1
