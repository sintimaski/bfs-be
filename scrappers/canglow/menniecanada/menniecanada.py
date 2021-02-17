from bs4 import BeautifulSoup
from cloudscraper import create_scraper

from scrappers.canglow.common.base_scrapper import BaseCanglowScrapper


class MennieCanadaScrapper(BaseCanglowScrapper):
    def __init__(self):
        super().__init__()

    def get_item(self, url):
        scrapper = create_scraper()
        resp = scrapper.get(url)
        soup = BeautifulSoup(markup=resp.text, features="html.parser")

        _type = url.strip("/")
        _type = _type.rsplit("/", 2)[1]
        _type = _type.replace("-", " ")
        type = _type.title()

        title_tag = soup.select_one("title")
        title = title_tag.text if title_tag else ""

        entry_title_tag = soup.select_one(".heading-text > h1.h1")
        entry_title = entry_title_tag.text if entry_title_tag else ""

        meta_description_tag = soup.select_one('meta[name="description"]')
        meta_description = (
            meta_description_tag.get("content", "")
            if meta_description_tag
            else ""
        )

        description_tag = soup.select_one(".uncode_text_column")
        description = description_tag.text if description_tag else ""

        _images = soup.select(".post-content img")
        images = [img.get("src") for img in _images if img.get("src")]
        images = list(set(images))

        available_sizes = str(soup.select_one(".uncont table"))

        data = {
            "type": type,
            "available_sizes": available_sizes,
            "title": title,
            "meta_description": meta_description,
            "entry_title": entry_title,
            "images": images,
            "alts": "",
            "description": description,
            "url": url,
        }
        return data

    def get_urls(self):
        scrapper = create_scraper()
        categories = [
            "https://menniecanada.com/products/mahogany-doors/",
            "http://menniecanada.com/products/oak-grain/",
            "https://menniecanada.com/products/smooth-doors/",
        ]
        base = "http://menniecanada.com"
        for category in categories:
            resp = scrapper.get(category)
            soup = BeautifulSoup(markup=resp.text, features="html.parser")
            items = soup.select(".post-content .col-link.custom-link")
            for item in items:
                href = item.get("href")
                if 'menniecanada' not in href:
                    href = f"{base}{href}"
                if href:
                    href = href.split("?")[0]
                    self.urls.append(href)
