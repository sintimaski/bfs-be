import json
import time
from concurrent.futures import ThreadPoolExecutor

import cloudscraper
import random

from core.proxies import proxies


def get_shop_items_from_api(item_data):
    time.sleep(random.uniform(1, 2))
    items_collected = []

    proxy_index = random.randint(0, len(proxies) - 1)
    proxy = {"http": proxies[proxy_index], "https": proxies[proxy_index]}

    scraper = cloudscraper.create_scraper()
    shop_slug = item_data["web_url"].strip("/").rsplit("/", 1)[1]

    shop_type_mapping = {
        "dispensary": "dispensaries",
        "delivery": "deliveries",
    }
    shop_type = shop_type_mapping[item_data["type"]]
    link = "https://api-g.weedmaps.com/discovery/v1/listings/{}/{}/menu_items?page_size=150&page={}&sort_by=name&sort_order=asc"
    data_presists = True
    total_menu_items = None
    page = 1
    while data_presists:
        time.sleep(random.uniform(0.25, 0.5))
        try:
            resp = scraper.get(
                link.format(shop_type, shop_slug, page), proxies=proxy
            )
            resp = json.loads(resp.text)
        except Exception as e:
            return {"failed": item_data}
        page += 1

        if "errors" in resp:
            break

        data = resp.get("data", {})
        menu_items = data.get("menu_items", [])
        total_menu_items = (
            resp.get("meta", {}).get("total_menu_items", 0)
            if not total_menu_items
            else total_menu_items
        )
        if not menu_items:
            break

        for item in menu_items:
            avatar_image = item.get("avatar_image", {})
            image_url = avatar_image.get("original_url", "")
            slug = item.get("slug", "")
            web_url = f"{item_data['web_url'].strip('/')}/menu/{slug}"

            new_item_data = {
                "name": item.get("name", ""),
                "weedmaps_id": str(item.get("id", "")),
                "image_url": image_url,
                "category": item.get("category", {}).get("name", ""),
                "edge_category": item.get("edge_category", {}) or {},
                "genetics_tag": item.get("genetics_tag", {}) or {},
                "prices": item.get("prices", {}) or {},
                "web_url": web_url,
                "shop_slug": shop_slug,
            }
            items_collected.append(new_item_data)
    return {"data": items_collected}


from core.models import WeedmapsProduct
from core.db_connector import db

# TODO move to helpers
from copy import deepcopy


def flatten_list(nested_list):
    nested_list = deepcopy(nested_list)
    while nested_list:
        sublist = nested_list.pop(0)
        if isinstance(sublist, list):
            nested_list = sublist + nested_list
        else:
            yield sublist


def get_items_from_api(api_collected):
    items_collected = {}
    passed = 0
    total = len(api_collected)
    items_failed = []
    with ThreadPoolExecutor(max_workers=8) as executor:
        for item_data in executor.map(get_shop_items_from_api, api_collected):
            passed += 1
            if "failed" not in item_data:
                print(f"{passed}/{total}", flush=True)
                for item in item_data["data"]:
                    prices = item["prices"]
                    prices.pop("grams_per_eighth", None)
                    if prices:
                        price_unit = list(prices.keys())[0]
                        prices_data = list(prices.values())
                        prices_data_flatten = flatten_list(prices_data)
                        prices_labels = [
                            price["label"] for price in prices_data_flatten
                        ]
                        prices = [
                            str(price["price"]) for price in prices_data_flatten
                        ]
                    else:
                        price_unit = ""
                        prices_labels = []
                        prices = []

                    # product = WeedmapsProduct.query.filter_by(
                    #     weedmaps_id=item['weedmaps_id']).first()
                    # if product:
                    #     continue
                    new_item = WeedmapsProduct(
                        name=item["name"],
                        shop_slug=item["shop_slug"],
                        image_url=item["image_url"],
                        category=item["category"],
                        web_url=item["web_url"],
                        prices=prices,
                        prices_labels=prices_labels,
                        price_unit=price_unit,
                        weedmaps_id=item["weedmaps_id"],
                    )
                    db.session.add(new_item)
                    db.session.commit()
            else:
                items_failed.append(item_data["failed"])
                print(f"{passed}/{total} - fail", flush=True)
    if items_failed:
        get_items_from_api(items_failed)
    return items_collected
