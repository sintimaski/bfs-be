from .leafly import LeaflyScrapper
from .gmaps import GmapsApiScrapper
from .weedmaps import WeedmapsAPIScrapper


class BFSUpdater:
    def __init__(self):
        self.scrappers = [
            LeaflyScrapper,
            GmapsApiScrapper,
            WeedmapsAPIScrapper
        ]

    def start_routine(self):
        self.start_scrapping()

    def start_scrapping(self):
        for scrapper in self.scrappers:
            scrapper.start_scrapping()

    def compare_to_new(self):
        pass
