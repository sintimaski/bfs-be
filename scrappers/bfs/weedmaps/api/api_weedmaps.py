import json
from concurrent.futures import ThreadPoolExecutor
from os import path
import cloudscraper
from sqlalchemy import and_

from app import app
from core.db_connector import db
from core.models import Business


class WeedmapsAPIScrapper:
    def __init__(self):
        self.source = "weedmaps"
        self.project = "encycloweedia"

        self.api_collected = []
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36"
        }
        current_file_dir = path.dirname(path.abspath(__file__))
        scrapper_dir = path.dirname(current_file_dir)
        self.files_dir = path.join(scrapper_dir, "files")
        self.links_collected = []

    def start_scrapping(self):
        self.get_data_from_api()

    def get_data_from_api(self):
        api_link = (
            "https://api-g.weedmaps.com/discovery/v1/listings?"
            "filter[plural_types][]=dispensaries&"
            "filter[plural_types][]=deliveries&"
            "filter[region_slug[dispensaries]]={}&"
            "filter[region_slug[deliveries]]={}&"
            "page_size={}&page={}&sort_by=name&sort_order=asc"
        )
        regions = self.get_regions_from_file()
        regions_passed = 0
        regions_total = len(regions)
        for region in regions:
            page = 1
            page_size = 150
            total_listings = None
            regions_passed += 1
            while True:
                scraper = cloudscraper.create_scraper()
                resp = scraper.get(
                    api_link.format(region, region, page_size, page),
                    headers=self.headers,
                )
                resp = json.loads(resp.text)
                page += 1

                if "errors" in resp:
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
                    type_map = {
                        "dispensary": "dispensaries",
                        "delivery": "deliveries",
                    }
                    base_url = (
                        "https://api-g.weedmaps.com/discovery/v1/listings/{}/{}"
                    )
                    slug = item.get("slug", "")
                    _type = type_map.get(item.get("type", ""), "")
                    self.links_collected.append(
                        f"{base_url.format(_type, slug)}"
                    )

                print(
                    f"{region} ({regions_passed}/{regions_total}): total - "
                    f"{total_listings}, passed - {page}"
                )

    def get_details(self):
        with ThreadPoolExecutor(max_workers=8) as executor:
            for shop_data in executor.map(
                self.get_shop_details, self.links_collected
            ):
                if self.business_exists(shop_data):
                    business = Business.query.filter(
                        and_(
                            Business.source_name__id
                            == shop_data.get("source_name__id", "")
                        )
                    ).first()
                    for key, value in shop_data.items():
                        setattr(business, key, value)
                else:
                    shop = Business(**shop_data)
                    db.session.add(shop)
                db.session.commit()

    def get_shop_details(self, link):
        scraper = cloudscraper.create_scraper()
        resp = scraper.get(
            link,
            headers=self.headers,
        )
        resp = json.loads(resp.text)
        item = resp.get("data", "")
        item = item.get("listing", "")

        item_data = {
            "source": self.source,
            "source_name__id": f'weedmaps_{item.get("id", "")}',
            "project": self.project,
            "name": item.get("name", ""),
            "category": item.get("type", ""),
            "subcategory": item.get("license_type", ""),
            "country": item.get("country", ""),
            "city": item.get("city", ""),
            "state": item.get("state", ""),
            "address": item.get("address", ""),
            "zip": item.get("zip_code", ""),
            "lat": item.GET("latitude", ""),
            "lng": item.GET("longitude", ""),
            "email": item.get("email", ""),
            "phone": item.get("phone", ""),
            "website": item.get("website", ""),
            "soc_fb": item.get("facebook_id", ""),
            "soc_tw": item.get("twitter_id", ""),
            "soc_ig": item.get("instagram_id", ""),
            "business_hours": item.get("business_hours", {}),
            "about": item.get("description", ""),
            "web_url": item.get("web_url", ""),
            "slug": item.get("slug", ""),
        }

        return item_data

    def get_regions_from_file(self):
        with open(path.join(self.files_dir, "regions.txt"), "r") as file:
            regions = file.readlines()

        regions = [
            region.strip("/").rsplit("/", 1)[1].strip() for region in regions
        ]
        return regions

    @staticmethod
    def business_exists(source_name__id):
        with app.app_context():
            exists = (
                Business.query.filter(
                    and_(Business.source_name__id == source_name__id)
                ).first()
                is not None
            )
        return exists
