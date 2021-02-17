import cloudscraper
from bs4 import BeautifulSoup

from scrappers.cars.getautofinance.common import PlazaLikeScrapper


class LeonsFineCarsScrapper(PlazaLikeScrapper):
    def __init__(self, project):
        source = "leonsfinecars"
        super().__init__(source, project)

    def get_cars_urls(self):
        base_url = "https://www.leonsfinecars.ca"
        listing_url = (
            "https://www.leonsfinecars.ca/used-inventory/index.htm{}"
        )
        start = "?start=0&"
        while True:
            scraper = cloudscraper.create_scraper()
            resp = scraper.get(
                listing_url.format(start), timeout=120
            )

            soup = BeautifulSoup(markup=resp.text, features="html.parser")
            urls_tags = soup.select('ul.inventoryList li.item a.url')
            for urls_tag in urls_tags:
                href = urls_tag.get('href')
                if href:
                    self.cars_urls.append(f"{base_url}{href}")

            start = soup.select_one('a[rel="next"]')
            if start:
                href = start.get('href')
                if href:
                    start = href
                    continue
            return
