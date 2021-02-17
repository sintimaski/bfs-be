import json

from scrappers.canglow.common.base_scrapper import BaseCanglowScrapper
from bs4 import BeautifulSoup
from cloudscraper import create_scraper


class GroupeNovaTechScrapper(BaseCanglowScrapper):
    def __init__(self):
        super().__init__()

    def get_item(self, url):
        scrapper = create_scraper()
        resp = scrapper.get(url)
        soup = BeautifulSoup(markup=resp.text, features="html.parser")

        title_tag = soup.select_one("title")
        title = title_tag.text if title_tag else ""

        entry_title_tag = soup.select_one(".product-name span")
        entry_title = entry_title_tag.text if entry_title_tag else ""

        meta_description_tag = soup.select_one('meta[name="description"]')
        meta_description = (
            meta_description_tag.get("content", "")
            if meta_description_tag
            else ""
        )

        details = ""
        details_headers = soup.select("div.item[data-role='collapsible']")
        for details_header in details_headers:
            if (
                details_header.select_one(".accord-heading").text
                != "Technical details"
            ):
                continue
            details_tag = details_header.find_next_sibling("div")
            if hasattr(details_tag, "attrs"):
                for attr in list(details_tag.attrs.keys()):
                    del details_tag[attr]

            for element in details_tag.recursiveChildGenerator():
                if hasattr(element, "attrs"):
                    for attr in list(element.attrs.keys()):
                        del element[attr]
            details = str(details_tag)

        custom_products = ""
        details_headers = soup.select("div.item[data-role='collapsible']")
        for details_header in details_headers:
            if (
                details_header.select_one(".accord-heading").text
                != "Custom Products"
            ):
                continue
            details_tag = details_header.find_next_sibling("div")
            if hasattr(details_tag, "attrs"):
                for attr in list(details_tag.attrs.keys()):
                    del details_tag[attr]

            for element in details_tag.recursiveChildGenerator():
                if hasattr(element, "attrs"):
                    for attr in list(element.attrs.keys()):
                        del element[attr]
            custom_products = str(details_tag)

        options = ""
        details_headers = soup.select("div.item[data-role='collapsible']")
        for details_header in details_headers:
            if details_header.select_one(".accord-heading").text != "Options":
                continue
            details_tag = details_header.find_next_sibling("div")
            if hasattr(details_tag, "attrs"):
                for attr in list(details_tag.attrs.keys()):
                    del details_tag[attr]

            for element in details_tag.recursiveChildGenerator():
                if hasattr(element, "attrs"):
                    for attr in list(element.attrs.keys()):
                        del element[attr]
            options = str(details_tag)

        description_tag = soup.select_one('[itemprop="description"]')
        description = description_tag.text if description_tag else ""

        img_data = str(soup).split("magnifierOpts", 1)[1]
        img_data = img_data.split("},\n", 1)[1]
        img_data = img_data.split("\n", 1)[0]
        img_data = img_data.strip()
        img_data = img_data.split('"data": ', 1)[1]
        img_data = img_data.rstrip(",")
        img_data_json = json.loads(img_data)
        images = [img["full"] for img in img_data_json]
        alts = [img["caption"] for img in img_data_json]

        base = "https://www.groupenovatech.com/"
        _images_design = soup.select("#container-packery-design a")
        _images = [
            f"{base}{img.get('href')}"
            for img in _images_design
            if img.get("href")
        ]
        _alts = [img.get("title") for img in _images_design if img.get("title")]
        images.extend(_images)
        alts.extend(_alts)

        data = {
            "title": title,
            "meta_description": meta_description,
            "entry_title": entry_title,
            "images": images,
            "alts": alts,
            "description": description,
            "options": options,
            "custom_products": custom_products,
            "details": details,
            "url": url,
        }
        return data

    def get_urls(self):
        scrapper = create_scraper()
        resp = scrapper.get(
            "https://www.groupenovatech.com/en_canada_ontario"
            "/products/entry-doors.html"
        )
        soup = BeautifulSoup(markup=resp.text, features="html.parser")
        items = soup.select(".product-item-info > a")
        for item in items:
            href = item.get("href")
            if href:
                self.urls.append(href)
