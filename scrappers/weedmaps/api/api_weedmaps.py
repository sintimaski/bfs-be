import json
from concurrent.futures import ThreadPoolExecutor
from os import path

import requests
from bs4 import BeautifulSoup


# GET WM PRODUCTS
# from core.models import WeedmapsShop, WeedmapsProduct
#
# product_shop_slugs = WeedmapsProduct.query\
#     .with_entities(WeedmapsProduct.shop_slug)\
#     .all()
# slugs = [product.shop_slug for product in product_shop_slugs]
# slugs = list(set(slugs))
# print(slugs)
#
# shops = WeedmapsShop.query\
#     .with_entities(WeedmapsShop.web_url, WeedmapsShop.type)\
#     .all()
# shops_data = []
# for shop in shops:
#     slug = shop.web_url.rsplit('/', 1)[1]
#     if slug not in slugs:
#         shops_data.append(
#             {
#                 "web_url": shop.web_url,
#                 "type": shop.type,
#             }
#         )
# print(len(shops_data))
# from test.items import get_items_from_api
# get_items_from_api(shops_data)

# GET WM SHOPS DETAILS
# from core.models import WeedmapsShop
# shops = WeedmapsShop.query\
#     .with_entities(WeedmapsShop.web_url)\
#     .filter(WeedmapsShop.phone.is_(None))\
#     .all()
# urls = []
# for shop in shops:
#     urls.append(shop.web_url)
# from test.test import get_shops_from_site
# get_shops_from_site(urls)

# GET WM PRODUCTS DETAILS
# from core.models import WeedmapsProduct
# products = WeedmapsProduct.query. \
#     with_entities(WeedmapsProduct.web_url). \
#     filter(WeedmapsProduct.details_collected.isnot(True))
# urls = []
# for product in products:
#     urls.append(product.web_url)
# from test.descriptions import get_items_descriptions
# get_items_descriptions(urls)


class WeedmapsAPIScrapper:
    def __init__(self):
        self.api_collected = []
        self.site_collected = []
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36"
        }
        current_file_dir = path.dirname(path.abspath(__file__))
        scrapper_dir = path.dirname(current_file_dir)
        self.files_dir = path.join(scrapper_dir, "files")

    def scrape_data(self):
        self.get_data_from_api()
        # self.get_data_from_api_file()
        # self.get_data_from_site()
        self.write_data()

    def get_item_from_site(self, item_data):
        item_collected = item_data.copy()
        resp = requests.get(item_collected["web_url"])
        soup = BeautifulSoup(resp.text, features="html.parser")
        print()

    def get_data_from_site(self):
        with ThreadPoolExecutor(max_workers=1) as executor:
            for item_data in executor.map(
                self.get_item_from_site, self.api_collected[:1]
            ):
                self.site_collected.append(item_data)

    def write_data(self):
        from core.models import WeedmapsShop
        from core.db_connector import db

        print(f"writing {len(self.api_collected)}")
        for item in self.api_collected:
            shop = WeedmapsShop.query.filter_by(
                weedmaps_id=item["weedmaps_id"]
            ).first()
            if shop:
                continue
            new_shop = WeedmapsShop(
                weedmaps_id=item["weedmaps_id"],
                business_name=item["business_name"],
                type=item["type"],
                category=item["category"],
                city=item["city"],
                address=item["address"],
                web_url=item["web_url"],
                slug=item["slug"],
            )
            db.session.add(new_shop)
            db.session.commit()

    def get_data_from_api_file(self):
        with open(path.join(self.files_dir, "api_results.json"), "r") as file:
            self.api_collected = json.loads(file.read())

    def get_regions_from_file(self):
        with open(path.join(self.files_dir, "regions.txt"), "r") as file:
            regions = file.readlines()

        # REMOVE THIS
        # regions = [
        #     region
        #     for region in regions
        #     if region.startswith('https://weedmaps.com/listings/in/canada/')
        # ]

        regions = [
            region.strip("/").rsplit("/", 1)[1].strip() for region in regions
        ]
        return regions

    def get_data_from_api(self):
        api_link = "https://api-g.weedmaps.com/discovery/v1/listings?filter[plural_types][]=dispensaries&filter[plural_types][]=deliveries&filter[region_slug[dispensaries]]={}&filter[region_slug[deliveries]]={}&page_size={}&page={}&sort_by=name&sort_order=asc"
        regions = self.get_regions_from_file()
        regions_passed = 0
        regions_total = len(regions)
        for region in regions:
            print(region)
            page = 1
            page_size = 150
            total_listings = None
            regions_passed += 1
            while True:
                resp = requests.get(
                    api_link.format(region, region, page_size, page),
                    headers=self.headers,
                )
                resp = json.loads(resp.text)
                page += 1

                if "errors" in resp:
                    print(resp)
                    break

                data = resp.get("data", {})
                listings = data.get("listings", [])
                total_listings = (
                    resp.get("meta", {}).get("total_listings", 0)
                    if not total_listings
                    else total_listings
                )
                if not listings:
                    break

                for item in listings:
                    item_data = {
                        "business_name": item.get("name", ""),
                        "weedmaps_id": str(item.get("id", "")),
                        "web_url": item.get("web_url", ""),
                        "address": item.get("address", ""),
                        "category": item.get("license_type", ""),
                        "type": item.get("type", ""),
                        "city": item.get("city", ""),
                        "slug": item.get("slug", ""),
                    }
                    self.api_collected.append(item_data)
                print(
                    f"{region} ({regions_passed}/{regions_total}): total - {total_listings}, passed - {page}"
                )

    def get_states(self):
        pass
