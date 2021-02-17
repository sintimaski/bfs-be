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


class DPAutoGroupScrapper(BaseCarScrapper):
    def __init__(self, project):
        source = "dpautogroup"
        source_id = "17484"
        tp = ThirdParty.query.filter(
            ThirdParty.name == "carnance_vinaudit"
        ).first()
        api_key = tp.api_key
        super().__init__(
            source=source,
            project=project,
            source_id=source_id,
            vinaudit_key=api_key,
        )

    def get_dealership_data(self, car_url: str):
        try:
            scraper = cloudscraper.create_scraper()
            resp = scraper.get(car_url)
            soup = BeautifulSoup(markup=resp.text, features="html.parser")

            sold = soup.select_one(".SoldVehicle")
            if sold:
                return {"out": car_url}

            product_name = get_element_text(soup, ".vehicleName")

            _del = soup.select_one(".PriceValue del")
            if _del:
                _del.extract()
            price = get_element_text(soup, ".PriceValue")
            price = price.replace("&nbsp", "")
            price = price.rsplit(".", 1)[0]
            price = "".join(c for c in price if c.isdigit())
            price = int(price)

            images_tags = soup.select("ul.slides img")
            images = []
            for image_tag in images_tags:
                images.append(image_tag.get("src", ""))

            options = []
            options_tags = soup.select(".VehicleOptions > li")
            for option in options_tags:
                options.append(option.text)

            content_tag = soup.select_one(
                "#standard-equipment > .panel-body > .row > div"
            )
            if content_tag:
                content_tag.attrs.clear()
                for tag in content_tag.select("*"):
                    if tag.name == "div":
                        tag.extract()
                    tag.attrs.clear()
            else:
                content_tag = ""

            details_soup = soup.select_one(".VehicleInfoDetails.row")
            # make = get_text_by_sibling(details_soup, "Make:")
            # model = get_text_by_sibling(details_soup, "Model:")
            year = get_text_by_sibling(details_soup, "Year:")
            # body_style = get_text_by_sibling(details_soup, "Body Style:")
            odometer = get_text_by_sibling(details_soup, "Odometer:")
            odometer = "".join([o for o in odometer if o.isdigit()])
            odometer = int(odometer)
            # engine = get_text_by_sibling(details_soup, "Engine:")

            # engine_size = get_text_by_sibling(details_soup, "Engine Size:")
            # engine_size = f"{engine_size}L"

            # driveline = get_text_by_sibling(details_soup, "Driveline:")
            exterior_color = get_text_by_sibling(
                details_soup, "Exterior Color:"
            )
            interior_color = get_text_by_sibling(
                details_soup, "Interior Color:"
            )
            # doors = get_text_by_sibling(details_soup, "Doors:")
            # passengers = get_text_by_sibling(details_soup, "Passengers:")
            # fuel = get_text_by_sibling(details_soup, "Fuel Type:")
            # city_fuel = get_text_by_sibling(details_soup, "City Fuel:")
            # hwy_fuel = get_text_by_sibling(details_soup, "Hwy Fuel:")
            stock_number = get_text_by_sibling(details_soup, "Stock Number:")
            vin = get_text_by_sibling(details_soup, "VIN:")
            vin = vin.upper()

            details_tags = soup.select(".seller_comments.row p")
            details = []
            for details_tag in details_tags:
                details.append(details_tag.text)
            details = "\n".join(details)

            location_diller_tag = soup.select_one(".details-page-address")
            location_diller_tag = "".join(
                [str(x) for x in location_diller_tag.contents]
            )
            location_diller_tag = str(location_diller_tag).split("<i ", 1)[0]
            ldt = location_diller_tag.split("<br/>")
            location_diller = " ".join(x.strip() for x in ldt)
            location_diller = " ".join(location_diller.split())

            # transmission = get_text_by_sibling(details_soup,
            #                                    "Transmission:").lower()
            # if 'automatic' in transmission:
            #     transmission = 'Automatic'
            # elif 'manual' in transmission:
            #     transmission = 'Manual'
            # elif 'tiptronic' in transmission:
            #     transmission = 'Tiptronic'

            car_data = {
                "source": self.source,
                "source_id": self.source_id,
                "product_name": product_name,
                "price": price,
                "images": images,
                # "make": make,
                # "model": model,
                "year": int(year),
                # "body_style": body_style,
                "odometer": odometer,
                # "transmission": transmission,
                # "engine": engine,
                # "engine_size": engine_size,
                # "driveline": driveline,
                "exterior_color": exterior_color,
                "interior_color": interior_color,
                # "doors": doors,
                # "passengers": passengers,
                # "fuel": fuel,
                # "city_fuel": city_fuel,
                # "hwy_fuel": hwy_fuel,
                "stock_number": stock_number,
                "vin": vin.strip(),
                "details": details,
                "options": options,
                "content": str(content_tag),
                "web_url": car_url,
                "location_diller": location_diller,
            }
            return car_data
        except Exception as e:
            print(traceback.format_exc())
            return {"failed": car_url}

    def get_cars_urls(self):
        base_url = "https://www.dpautogroup.com"
        listing_url = "https://www.dpautogroup.com/used-cars/?ppage=50&cpage={}"
        page = 1
        while True:
            scraper = cloudscraper.create_scraper()
            resp = scraper.get(listing_url.format(page))
            soup = BeautifulSoup(markup=resp.text, features="html.parser")
            cars_urls_tags = soup.select(
                "div.vehicle.search-result-item.vehicleList a"
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
