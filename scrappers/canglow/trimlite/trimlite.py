from time import sleep

from bs4 import BeautifulSoup
from cloudscraper import create_scraper
import random

from scrappers.canglow.common.base_scrapper import BaseCanglowScrapper


class TrimliteScrapper(BaseCanglowScrapper):
    def __init__(self):
        super().__init__()

    def get_item(self, url):
        scrapper = create_scraper()
        resp = scrapper.get(url)
        soup = BeautifulSoup(markup=resp.text, features="html.parser")

        rel_prod = soup.select_one(".related.products")
        if rel_prod:
            rel_prod.extract()

        title_tag = soup.select_one("title")
        title = title_tag.text if title_tag else ""

        entry_title_tag = soup.select_one("h2.entry-title")
        entry_title = entry_title_tag.text if entry_title_tag else ""

        breadcrumbs = soup.select(".fusion-breadcrumb-item span")
        type = breadcrumbs[1].text
        category = breadcrumbs[2].text
        series = breadcrumbs[3].text
        if series == entry_title:
            series = ""

        meta_description_tag = soup.select_one('meta[name="description"]')
        meta_description = (
            meta_description_tag.get("content", "")
            if meta_description_tag
            else ""
        )

        description = ""
        description_tag = soup.select_one(
            ".woocommerce-product-details__short-description"
        )
        if description_tag:
            for a_tag in description_tag.select("a"):
                a_tag.extract()
            description = description_tag.text if description_tag else ""

        data = {
            "title": title,
            "meta_description": meta_description,
            "entry_title": entry_title,
            "description": description,
            "url": url,
            "type": type,
            "category": category,
            "series": series,
        }

        if "doorlites" in url:
            privacy = ""
            _privacy = soup.find(
                "th",
                {"class": "woocommerce-product-attributes-item__label"},
                string="Privacy",
            )
            if _privacy:
                _privacy = _privacy.parent
                _privacy = _privacy.select_one(
                    ".woocommerce-product-attributes-item__value"
                )
                privacy = _privacy.text if _privacy else ""

            eef = ""
            _eef = soup.find(
                "th",
                {"class": "woocommerce-product-attributes-item__label"},
                string="Energy Efficiency",
            )
            if _eef:
                _eef = _eef.parent
                _eef = _eef.select_one(
                    ".woocommerce-product-attributes-item__value"
                )
                eef = _eef.text if _eef else ""

            gd = ""
            _gd = soup.find(
                "th",
                {"class": "woocommerce-product-attributes-item__label"},
                string="Glass Details",
            )
            if _gd:
                _gd = _gd.parent
                _gd = _gd.select_one(
                    ".woocommerce-product-attributes-item__value"
                )
                gd = _gd.text if _gd else ""

            qss = ""
            _qss = soup.find(
                "th",
                {"class": "woocommerce-product-attributes-item__label"},
                string="Doorlite Sizes",
            )
            if _qss:
                _qss = _qss.parent
                _qss = _qss.select_one(
                    ".woocommerce-product-attributes-item__value"
                )
                qss = _qss.text if _qss else ""

            sos = ""
            _sos = soup.find(
                "th",
                {"class": "woocommerce-product-attributes-item__label"},
                string="Frame Details",
            )
            if _sos:
                _sos = _sos.parent
                _sos = _sos.select_one(
                    ".woocommerce-product-attributes-item__value"
                )
                sos = _sos.text if _sos else ""

            _images = soup.select(".product img")
            images = [img.get("src") for img in _images if img.get("src")]
            alts = [img.get("alt") for img in _images if img.get("alt")]

            data.update(
                {
                    "privacy": privacy,
                    "images": images,
                    "alts": alts,
                    "energy_efficiency": eef,
                    "glass_details": gd,
                    "doorlite_sizes": qss,
                    "frame_details": sos,
                }
            )
        elif "exterior-doors" in url:
            _images = soup.select(".woocommerce-product-gallery__image a")
            images = [img.get("href") for img in _images if img.get("href")]
            qss = ""
            _qss = soup.find(
                "th",
                {"class": "woocommerce-product-attributes-item__label"},
                string="Quick Ship Sizes",
            )
            if _qss:
                _qss = _qss.parent
                _qss = _qss.select_one(
                    ".woocommerce-product-attributes-item__value"
                )
                qss = _qss.text if _qss else ""

            sos = ""
            _sos = soup.find(
                "th",
                {"class": "woocommerce-product-attributes-item__label"},
                string="Special Order Sizes",
            )
            if _sos:
                _sos = _sos.parent
                _sos = _sos.select_one(
                    ".woocommerce-product-attributes-item__value"
                )
                sos = _sos.text if _sos else ""

            data.update(
                {
                    "quick_ship_sizes": qss,
                    "special_order_sizes": sos,
                    "images": images,
                }
            )

        return data

    def get_urls(self):
        scrapper = create_scraper()
        categories = [
            "https://www.trimlite.com/product-category/exterior-doors/",
            "https://www.trimlite.com/product-category/doorlites/",
        ]

        series = []
        for category in categories:
            resp = scrapper.get(category)
            soup = BeautifulSoup(markup=resp.text, features="html.parser")
            items = soup.select("ul.products-5 li a")
            for item in items:
                href = item.get("href")
                if href:
                    href = href.split("?")[0]
                    series.append(href)

        doors = []
        for type in series:
            resp = scrapper.get(type)
            soup = BeautifulSoup(markup=resp.text, features="html.parser")
            items = soup.select("ul.products li a")
            for item in items:
                href = item.get("href")
                if href:
                    href = href.split("?")[0]
                    doors.append(href)
                    # self.urls.append(href)

        doors = list(set(doors))

        for door in doors:
            resp = scrapper.get(door, timeout=30)
            soup = BeautifulSoup(
                markup=resp.text, features="html.parser"
            )
            cat = soup.select_one(".term-description")
            print(f"series: {cat is not None}, {door}")
            if cat is not None:
                items = soup.select("ul.products li a")
                for item in items:
                    href = item.get("href")
                    if href:
                        href = href.split("?")[0]
                        self.urls.append(href)
                        print(f"              {href}")
            else:
                self.urls.append(door)

        self.urls = list(set(self.urls))
