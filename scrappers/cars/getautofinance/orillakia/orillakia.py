import json

import cloudscraper

from scrappers.cars.getautofinance.common import PlazaLikeScrapper


class OrillaKiaScrapper(PlazaLikeScrapper):
    def __init__(self, project):
        source = "orilliakia"
        super().__init__(source, project)

    def get_cars_urls(self):
        base_url = "https://www.orilliakia.com"
        listing_url = (
            "https://www.orilliakia.com/apis/widget/"
            "INVENTORY_LISTING_DEFAULT_AUTO_ALL:"
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
