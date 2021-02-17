import json
import time
from concurrent.futures import ThreadPoolExecutor

import cloudscraper
import random
from bs4 import BeautifulSoup

from core.proxies import proxies


def get_item_description(url):
    time.sleep(random.uniform(1, 2.5))
    proxy_index = random.randint(0, len(proxies) - 1)
    proxy = {"http": proxies[proxy_index], "https": proxies[proxy_index]}

    scraper = cloudscraper.create_scraper(delay=10)
    link = url.strip("/")
    resp = None

    try:
        resp = scraper.get(
            link,
            proxies=proxy,
        )
    except Exception as e:
        print(e)
        return {"failed": link}

    source = resp.text
    soup = BeautifulSoup(source, features="html.parser")

    try:
        data_tag = soup.select_one("script#__NEXT_DATA__")
        data = json.loads(data_tag.string)
        product = data.get("props", {}).get("product", {})
        image_url = product.get("avatar_image", {}).get("original_url", "")
        short_description = product.get("body", "")

        strain_info = data.get("props", {}).get("strainInfo", {})
        description = strain_info.get("description", "")
        effects_data = strain_info.get("effects", [])
        effects = [effect["name"] for effect in effects_data]
        flavors_data = strain_info.get("flavors", [])
        flavors = [flavor["name"] for flavor in flavors_data]

        item_collected = {
            "web_url": url,
            "description": description,
            "short_description": short_description,
            "image_url": image_url,
            "strain_effects": effects,
            "strain_flavours": flavors,
        }
        return item_collected
    except Exception as e:
        with open("test.html", "w+") as file:
            file.write(source)
        return {"failed": link}


from core.models import WeedmapsProduct
from core.db_connector import db


def get_items_descriptions(urls):
    passed = 0
    failed = 0
    total = len(urls)
    urls_failed = []
    with ThreadPoolExecutor(max_workers=8) as executor:
        for item_data in executor.map(get_item_description, urls):
            passed += 1
            if "failed" not in item_data:
                print(f"{passed}/{total}", flush=True)
                product = WeedmapsProduct.query.filter(
                    WeedmapsProduct.web_url == item_data["web_url"]
                ).first()
                product.description = item_data["description"]
                product.image_url = item_data["image_url"]
                product.short_description = item_data["short_description"]
                product.strain_effects = item_data["strain_effects"]
                product.strain_flavours = item_data["strain_flavours"]
                product.details_collected = True
                db.session.commit()
            else:
                failed += 1
                urls_failed.append(item_data["failed"])
                print(
                    f"{passed}/{total} - fail ({failed}, {failed / passed * 100}%)",
                    flush=True,
                )
    if urls_failed:
        get_items_descriptions(urls_failed)
