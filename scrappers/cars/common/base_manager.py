from typing import Dict, List


DEV_TOKEN_KEY = "dev"
PROD_TOKEN_KEY = "prod"


class BaseCarManager:
    def __init__(self, scrappers: List, tokens: Dict) -> None:

        self.scrappers = scrappers
        self.dealerships = []
        for scrapper_class in self.scrappers:
            scrapper = scrapper_class()
            self.dealerships.append(scrapper.source)

        self.dev_token = tokens.get(DEV_TOKEN_KEY)
        self.prod_token = tokens.get(PROD_TOKEN_KEY)

        self.post_car_url = (
            "https://getautofinance.ca/wp-json/jwa-cars-listing/v1/cars/"
        )
