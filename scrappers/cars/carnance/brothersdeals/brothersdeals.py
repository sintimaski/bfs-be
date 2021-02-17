import traceback

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


class BrothersDealsScrapper(BaseCarScrapper):
    def __init__(self, project):
        source = "brothersdeals"
        source_id = "43384"
        tp = ThirdParty.query.filter(
            ThirdParty.name == "carnance_vinaudit"
        ).first()
        api_key = tp.api_key
        super().__init__(
            source=source,
            project=project,
            source_id=source_id,
            vinaudit_key=api_key,
            force_carsxe=True
        )

    def get_dealership_data(self, car_url: str):
        try:
            scraper = cloudscraper.create_scraper()
            resp = scraper.get(car_url)
            soup = BeautifulSoup(markup=resp.text, features="html.parser")

            product_name = get_element_text(soup, ".print__title")

            price = soup.select_one("#js-calc-price")
            price = price.get("value", 0) if price else 0
            price = "".join(c for c in price if c.isdigit())
            price = int(price)

            images_tags = soup.select("ul#js-gallery img")
            images = []
            for image_tag in images_tags:
                images.append(image_tag.get("src", ""))

            options = []
            options_tags = soup.select("#features ul.bullet-list li")
            for option in options_tags:
                options.append(option.text)

            year = soup.select_one(
                "#custom_form__ask_about_vehicle_vehicle_year"
            )
            year = year.get("value", "") if year else ""
            year = "".join(c for c in year if c.isdigit())
            year = int(year)

            odometer = soup.select_one(".icon--dashboard")
            odometer = odometer.parent.select_one("strong")
            odometer = odometer.text if odometer else ""
            odometer = "".join([o for o in odometer if o.isdigit()])
            odometer = int(odometer) if odometer else 0

            stock_number = soup.select_one(
                "#custom_form__ask_about_vehicle_vehicle_stock"
            )
            stock_number = stock_number.get("value", "") if stock_number else ""

            _vin = resp.text.split("vehicle_vin=", 1)[1]
            vin = _vin.split('">', 1)[0]

            exterior_color = ""
            _exterior_color = soup.find("strong", string="Exterior Colour")
            if _exterior_color:
                _exterior_color = _exterior_color.parent.parent
                exterior_color = _exterior_color.select_one("dd li")
                exterior_color = (
                    exterior_color.text if exterior_color else exterior_color
                )

            details_tags = soup.select_one("pre.pre-content")
            details = details_tags.text if details_tags else ""

            car_data = {
                "source": self.source,
                "source_id": self.source_id,
                "product_name": product_name,
                "price": price,
                "images": images,
                "year": year,
                "odometer": odometer,
                "exterior_color": exterior_color,
                "stock_number": stock_number,
                "vin": vin,
                "details": details,
                "options": options,
                "web_url": car_url,
            }
            return car_data
        except Exception as e:
            print(traceback.format_exc())
            return {"failed": car_url}

    def get_cars_urls(self):
        base_url = "https://www.brothersdeals.com"
        listing_url = "https://www.brothersdeals.com/vehicles/?p={}"
        page = 1
        while True:
            scraper = cloudscraper.create_scraper()
            resp = scraper.get(listing_url.format(page))
            soup = BeautifulSoup(markup=resp.text, features="html.parser")
            cars_urls_tags = soup.select(
                'div.container[aria-labelledby="SearchResults"] h4 a'
            )
            if not cars_urls_tags:
                break
            for car_url_tag in cars_urls_tags:
                if (
                    f'{base_url}{car_url_tag.get("href", "")}'
                    not in self.cars_urls
                ):
                    self.cars_urls.append(
                        f'{base_url}{car_url_tag.get("href", "")}'
                    )
            page += 1
        return self.cars_urls
