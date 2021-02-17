from bs4 import BeautifulSoup
from cloudscraper import create_scraper

from scrappers.canglow.common.base_scrapper import BaseCanglowScrapper


class FusionGlassScrapper(BaseCanglowScrapper):
    def __init__(self):
        super().__init__()

    def get_item(self, url):
        scrapper = create_scraper()
        resp = scrapper.get(url)
        soup = BeautifulSoup(markup=resp.text, features="html.parser")

        title_tag = soup.select_one("title")
        title = title_tag.text if title_tag else ""

        meta_description_tag = soup.select_one('meta[name="description"]')
        meta_description = (
            meta_description_tag.get("content", "")
            if meta_description_tag
            else ""
        )

        entry_title_tag = soup.select_one(".et_pb_text_inner > h1 > span")
        entry_title = entry_title_tag.text if entry_title_tag else ""

        type_tag = soup.select_one(".et_pb_text_inner > p > strong > span")
        type = type_tag.text if type_tag else ""

        description_tag = soup.select_one(".et_pb_text_inner > p > span > span")
        description = description_tag.text if description_tag else ""

        _privacy = soup.select_one(".et_pb_text_inner")
        _privacy = str(_privacy).split("●", 1)[0]
        privacy = _privacy.count("○") + 1

        _images = soup.select(".et_builder_inner_content img")
        images = [img.get("src") for img in _images if img.get("src")]
        images = list(set(images))

        data = {
            "type": type,
            "privacy": privacy,
            "title": title,
            "meta_description": meta_description,
            "entry_title": entry_title,
            "images": images,
            "description": description,
            "url": url,
        }
        return data

    def get_urls(self):
        scrapper = create_scraper()
        categories = [
            "https://fusion-glass.com/traditional-glass-collection/",
            "https://fusion-glass.com/contemporary-glass-collection/",
            "https://fusion-glass.com/absolute-glass-collection/",
            "https://fusion-glass.com/wrought-iron-glass-collection/",
            # "https://fusion-glass.com/dual-glazed-collection/",
            # "https://fusion-glass.com/sandblast-glass-collection-2/",
        ]
        for category in categories:
            resp = scrapper.get(category)
            soup = BeautifulSoup(markup=resp.text, features="html.parser")
            items = soup.select(".et_pb_image_wrap")
            for item in items:
                item = item.parent
                href = item.get("href")
                if href and "http" in href:
                    href = href.split("?")[0]
                    self.urls.append(href)
