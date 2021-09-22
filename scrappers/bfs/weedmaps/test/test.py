import json
import random
import time
import traceback
from concurrent.futures import ThreadPoolExecutor

import cloudscraper
import urllib3
from bs4 import BeautifulSoup
from requests.exceptions import ProxyError

from random_user_agent.params import OperatingSystem, SoftwareName
from random_user_agent.user_agent import UserAgent
from core.proxies import proxies

_proxies = list(set(proxies))


def get_shop_data_from_site(url):
    time.sleep(random.uniform(1.5, 2.5))
    item_collected = {}
    proxy_index = random.randint(0, len(_proxies) - 1)
    proxy = {"http": _proxies[proxy_index], "https": _proxies[proxy_index]}

    mobile = random.choice([True, False])
    platforms = ["android", "ios"] if mobile else ["darwin", "windows"]
    platform = random.choice(platforms)
    browser = None if mobile else random.choice(["firefox", "chrome"])
    scraper = cloudscraper.create_scraper(
        delay=5,
        # interpreter='nodejs',
        # captcha={
        #     'provider': 'anticaptcha',
        #     'api_key': 'a18f1f5792f0ea9a994d409948eab4f0',
        #     'no_proxy ': True
        # },
        # browser={
        #     'browser': browser,
        #     'platform': platform,
        #     'mobile': mobile
        # }
    )
    link = url.strip("/")

    try:
        resp = scraper.get(
            f"{link}/about",
            proxies=proxy,
        )
    except Exception as e:
        return {"failed": link, "proxy": proxy["https"], "platform": platform}

    source = resp.text
    soup = BeautifulSoup(source, features="html.parser")

    try:
        data_holder = soup.find("script", type="application/ld+json")
        data_string = data_holder.string
        data = json.loads(data_string)

        phone = data.get("telephone", "")
        website = data.get("url", "")
        address = data.get("address", {}).get("streetAddress", "")
        email = data.get("email", "").split("mailto:", 1)[1]

        business_hours_raw = data.get("openingHoursSpecification", [])
        business_hours = []
        for day in business_hours_raw:
            day.pop("@type", None)
            business_hours.append(day)

        services_tag = soup.select_one('div[data-testid="service-type"]')
        services = services_tag.text if services_tag else ""

        intro_tag = soup.select_one('div[data-test-id="truncated-intro"]')
        intro = intro_tag.text if intro_tag else ""

        aboutus_tag = soup.select_one(
            'div[data-test-id="truncated-description"]'
        )
        aboutus = aboutus_tag.text if aboutus_tag else ""

        amenities_tags = soup.select(
            'div[data-test-id="section-amenities"] > div > div'
        )
        amenities = []
        for amenity_tag in amenities_tags:
            amenities.append(amenity_tag.text)

        f_t_announcement_tag = soup.select_one(
            'div[data-test-id="listing-details-ftp-announcement"]'
        )
        f_t_announcement = (
            f_t_announcement_tag.text if f_t_announcement_tag else ""
        )

        announcement_tag = soup.select_one(
            'div[data-test-id="listing-details-announcement"]'
        )
        announcement = announcement_tag.text if announcement_tag else ""
        item_collected.update(
            {
                "web_url": url,
                "phone": phone,
                "website": website,
                "address": address,
                "email": email,
                "business_hours": business_hours,
                "intro": intro,
                "services": services,
                "aboutus": aboutus,
                "amenities": amenities,
                "f_t_announcement": f_t_announcement,
                "announcement": announcement,
                "proxy": proxy,
            }
        )
        return item_collected
    except Exception as e:
        return {"failed": link, "proxy": proxy["https"], "platform": platform}


from core.models import WeedmapsShop
from core.db_connector import db


def get_shops_from_site(urls):
    passed = 0
    total = len(urls)
    failed = []
    with ThreadPoolExecutor(max_workers=8) as executor:
        for item_data in executor.map(get_shop_data_from_site, urls):
            passed += 1
            if "failed" in item_data:
                failed.append(item_data["failed"])
                print(
                    f"{passed}/{total} - fail({len(failed) / passed * 100}), {item_data.get('proxy')} {item_data.get('platform')}"
                )
            else:
                product = WeedmapsShop.query.filter_by(
                    web_url=item_data["web_url"]
                ).first()
                product.phone = item_data["phone"]
                product.website = item_data["website"]
                product.address = item_data["address"]
                product.email = item_data["email"]
                product.business_hours = item_data["business_hours"]
                product.intro = item_data["intro"]
                product.services = item_data["services"]
                product.aboutus = item_data["aboutus"]
                product.amenities = item_data["amenities"]
                product.f_t_announcement = item_data["f_t_announcement"]
                product.announcement = item_data["announcement"]
                db.session.commit()
                print(f"{passed}/{total} - success({item_data['proxy']})")
    if failed:
        get_shops_from_site(failed)


def get_shop_items_from_site(item_data):
    weedmaps_id = item_data["weedmaps_id"]
    items_collected = []

    scraper = cloudscraper.create_scraper()
    shop_slug = item_data["web_url"].strip("/").rsplit("/", 1)[1]
    link = "https://api-g.weedmaps.com/discovery/v1/listings/dispensaries/{}/menu_items?include[]=facets.categories&page_size=150&page={}&sort_by=name&sort_order=asc"
    data_presists = True
    total_menu_items = None
    page = 1
    while data_presists:
        resp = scraper.get(link.format(shop_slug, page))
        resp = json.loads(resp.text)
        page += 1

        if "errors" in resp:
            data_persist = False
            break

        data = resp.get("data", {})
        menu_items = data.get("menu_items", [])
        total_menu_items = (
            resp.get("meta", {}).get("total_menu_items", 0)
            if not total_menu_items
            else total_menu_items
        )
        if not menu_items:
            data_persist = False
            break

        for item in menu_items:
            avatar_image = item.get("avatar_image", {}) or {}
            image_url = item.get("original_url", "")
            slug = item.get("slug", "")
            web_url = f"{item_data['web_url'].strip('/')}/menu/{slug}"

            new_item_data = {
                "name": item.get("name", ""),
                "image_url": image_url,
                "category": item.get("category", {}) or {},
                "edge_category": item.get("edge_category", {}) or {},
                "genetics_tag": item.get("genetics_tag", {}) or {},
                "prices": item.get("prices", {}) or {},
                "web_url": web_url,
            }
            items_collected.append(new_item_data)

    return {weedmaps_id: items_collected}


def get_items_from_site(api_collected):
    items_collected = []
    passed = 0
    total = len(api_collected)
    with ThreadPoolExecutor(max_workers=8) as executor:
        for item_data in executor.map(get_shop_items_from_site, api_collected):
            items_collected.append(item_data)
            passed += 1
            print(f"{passed}/{total}")
    return items_collected
