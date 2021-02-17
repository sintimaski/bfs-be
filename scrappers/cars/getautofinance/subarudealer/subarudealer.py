import json
from typing import Dict

import cloudscraper
from bs4 import BeautifulSoup

from scrappers.cars.getautofinance.common import (
    PlazaLikeScrapper,
    get_element_text,
)


class SubaruDealerScrapper(PlazaLikeScrapper):
    def __init__(self, project):
        source = "subarudealer"
        super().__init__(source, project)

    def get_dealership_data(self, car_url) -> Dict:
        try:
            scraper = cloudscraper.create_scraper()
            resp = scraper.get(car_url)
            resp_text = str(resp.text)
            soup = BeautifulSoup(markup=resp.text, features="html.parser")

            product_name = get_element_text(soup, ".pre_owned_vehicle_title")

            pdc = soup.select_one("#POS_Detail_Container")

            make = pdc.get("data-make", "")
            model = pdc.get("data-model-name", "")
            trim = pdc.get("data-trim-name", "")
            stock_number = pdc.get("data-stockcode", "")
            vin = pdc.get("data-vin", "")
            transmission = pdc.get("data-transmission", "")
            exterior_color = pdc.get("data-exterior", "")
            interior_color = pdc.get("data-interior", "")

            year = pdc.get("data-model-year")
            year = int(year) if year else None

            price = pdc.get("data-price", "")
            price = "".join([p for p in price if p.isnumeric()])
            price = int(price) if price else None

            odometer = pdc.get("data-odometer", "")
            odometer = "".join([o for o in odometer if o.isnumeric()])
            odometer = int(odometer) if odometer else None

            _images_tag = resp_text.split('<div id="ivJSON">', 1)[1]
            _images_json = _images_tag.split("</div>", 1)[0] or {}
            images_json = json.loads(_images_json)
            images_list = images_json.get("Images", [])
            images = [image["full"] for image in images_list]

            options_tags = soup.select(".preowned_specs > li")
            options = [
                o.text for o in options_tags if "notavailable" not in o.text
            ]

            details = get_element_text(
                soup, ".pre_owned_open_div .marginTop.marginBottom"
            )

            engine = ""
            labels = soup.select('.pre_owned_specs_col1.label')
            for label in labels:
                if label.text == 'Engine Type':
                    par = label.parent.select_one('.pre_owned_specs_col2')
                    engine = par.text if par else ''


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
                "details": details,
                "options": options,
                "web_url": car_url,
            }
            return car_data
        except Exception as e:
            return {"failed": car_url}

    def get_cars_urls(self):
        base_url = (
            "https://www.orillia.subarudealer.ca/WebPage.aspx?"
            "WebSiteID=226&WebPageID=4748"
        )
        listing_url = (
            "https://www.orillia.subarudealer.ca/api/used-car/"
            'get-inventory?criteria={{"ownerIds":"7721",'
            '"siteType":1,"model":"","price":{{"MinValue":"0",'
            '"MaxValue":"100000"}},"bodyType":"","yearRange":{{'
            '"MinValue":"2013","MaxValue":"2020"}},"kilometerRange"'
            ':{{"MinValue":"10","MaxValue":"144758"}},'
            '"transmissionType":"Any","certified":"N","pageSize":{}'
            ',"pageNumber":{},"latitude":0,"longitude":0,"distance"'
            ':0,"languageCode":"en-ca","engineTypeId":0,"bodyColor"'
            ':"","option":""}}&location=undefined&'
            "sortExpression=LowestPrice"
        )
        start_page = 1
        page_size = 20
        while True:
            scraper = cloudscraper.create_scraper()
            resp = scraper.get(
                listing_url.format(page_size, start_page), timeout=120
            )
            data = json.loads(resp.text)
            inventory = data["UsedVehicles"]

            for item in inventory:
                car_url = f"{base_url}&" f'UsedCarID={item["OwnerCarId"]}'
                self.cars_urls.append(car_url)

            total_page = data["TotalPage"]
            if start_page >= total_page:
                break
            start_page += 1
