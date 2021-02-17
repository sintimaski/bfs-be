import cloudscraper
from bs4 import BeautifulSoup

from scrappers.cars.getautofinance.common import PlazaLikeScrapper


class Hwy11RamScrapper(PlazaLikeScrapper):
    def __init__(self, project):
        source = "hwy11ram"
        super().__init__(source, project)

    def get_cars_urls(self):
        base_url = "https://www.hwy11ram.com"
        listing_url = "https://www.hwy11ram.com/all-inventory/index.htm{}"
        next_param = ""
        while True:
            scraper = cloudscraper.create_scraper()
            resp = scraper.get(listing_url.format(next_param), timeout=120)
            soup = BeautifulSoup(resp.text, features="html.parser")

            cars_urls_tags = soup.select("a.url")
            for car_url_tag in cars_urls_tags:
                self.cars_urls.append(
                    f'{base_url}{car_url_tag.get("href", "")}'
                )

            next_tag = soup.select_one("a[rel='next']")
            if not next_tag or next_tag.get("href", "") == next_param:
                break
            next_param = next_tag.get("href", "")
