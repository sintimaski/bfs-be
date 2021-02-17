from .api.api_weedmaps import WeedmapsAPIScrapper


def scrape_data():
    scrapper = WeedmapsAPIScrapper()
    scrapper.scrape_data()


# if __name__ == "__main__":
#     scrape_data()
