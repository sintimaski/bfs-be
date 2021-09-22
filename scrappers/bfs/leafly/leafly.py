import json

import cloudscraper
import random

from core.db_connector import db
from core.models import Business
from core.proxies import proxies


class LeaflyScrapper:
    def __init__(self):
        self.source = "leafly"
        self.project = "encycloweedia"

    def start_scrapping(self):
        page = 1
        limit = 100
        api_link = (
            "https://web-finder.leafly.com/api/get-dispensaries?"
            "userLat=36.1699412&userLon=-115.1398296&countryCode=US&"
            "retailType=dispensary&sort=default&geoQueryType=point&"
            "radius=1000000.109690296341793mi&page={}&limit={}&"
            "strainFilters=true"
        )
        failed = []
        while True:
            scraper = cloudscraper.create_scraper()
            resp = scraper.get(api_link.format(page, limit))
            data = json.loads(resp.text)
            stores = data.get("stores", [])
            if not len(stores):
                break
            store_num = 0
            for store in stores:
                print(f"store {store_num}/{len(stores)}")
                store_num += 1
                result = self.get_dispensary(store)
                if "error" in result:
                    failed.append(store["slug"])
            print(f"{page}/{data['pageCount']} pages. Limit {limit}.")
            page += 1

    def get_dispensary(self, data):
        try:
            base_url = "https://www.leafly.com/dispensary-info/{}"
            web_url = base_url.format(data["slug"])
            scraper = cloudscraper.create_scraper()

            proxy_index = random.randint(0, len(proxies) - 1)
            proxy = {
                "http": proxies[proxy_index],
                "https": proxies[proxy_index],
            }
            resp = scraper.get(web_url, proxies=proxy)
            if resp.status_code != 200:
                return

            next_data_text = resp.text.split(
                '<script id="__NEXT_DATA__" type="application/json">', 1
            )[1]
            next_data_text = next_data_text.split("</script>", 1)[0]
            next_data = json.loads(next_data_text)

            props = next_data.get("props", {})
            page_props = props.get("pageProps", {})
            dispensary = page_props.get("dispensary", {})
            geolocation = page_props.get("geolocation", {})

            subcategory = (
                "medical"
                if data["medical"]
                else ("recreational" if data["recreational"] else "")
            )
            source_name__id = f"{self.source}_{data['id']}"
            result_data = {
                "source_name__id": source_name__id,
                "project": self.project,
                "name": data["name"],
                "source": self.source,
                "category": data["retailType"],
                "subcategory": subcategory,
                "business_hours": data["schedule"],
                "web_url": web_url,
                "slug": data["slug"],
                "website": dispensary["website"],
                "email": dispensary["email"],
                "phone": data["phone"],
                "country": geolocation["country_code"],
                "state": geolocation["state_code"],
                "city": data["city"],
                "address": data["address1"],
                "address_2": data["address2"],
                "zip": data["zip"],
                "lat": data["primaryLocation"]["lat"],
                "lng": data["primaryLocation"]["lon"],
                "about": dispensary["description"],
            }

            existing = Business.query.filter(
                Business.source_name__id == source_name__id
            ).first()
            if existing:
                for key, value in result_data.items():
                    setattr(existing, key, value)
                db.session.commit()
            else:
                new_business = Business(**result_data)
                db.session.add(new_business)
                db.session.commit()
            return {"success": data["slug"]}
        except Exception as e:
            return {"error": data["slug"]}
