from scrappers.canglow.common.base_scrapper import BaseCanglowScrapper
from bs4 import BeautifulSoup
from cloudscraper import create_scraper


class OdlScrapper(BaseCanglowScrapper):
    def __init__(self):
        super().__init__()

    def get_item(self, url):
        scrapper = create_scraper()
        resp = scrapper.get(url)
        soup = BeautifulSoup(markup=resp.text, features="html.parser")

        title_tag = soup.select_one("title")
        title = title_tag.text if title_tag else ""

        entry_title_tag = soup.select_one(".product-info-title > h1")
        entry_title = entry_title_tag.text if entry_title_tag else ""

        meta_description_tag = soup.select_one('meta[name="description"]')
        meta_description = (
            meta_description_tag.get("content", "")
            if meta_description_tag
            else ""
        )

        description_tag = soup.select_one(
            "#hs_cos_wrapper_module_1565295816093468 p"
        )
        description = description_tag.text if description_tag else ""

        _images = soup.select('.product-gallery-main img')
        images = [img.get('src') for img in _images if img.get('src')]
        alts = [img.get('alt') for img in _images if img.get('alt')]

        _gt = soup.find('h3', string='Glass Textures')
        if _gt:
            _gt = _gt.parent.parent.parent
            _gt_images = _gt.select('.acc-content img')
            gt_images = [img.get('src') for img in _gt_images if img.get('src')]
            gt_alts = [img.get('alt') for img in _gt_images if img.get('alt')]
            images.extend(gt_images)
            alts.extend(gt_alts)

        _dg = soup.find('h3', string='Door Glass')
        if _dg:
            _dg = _dg.parent.parent.parent
            _dg_images = _dg.select('.acc-content .door-img img')
            dg_images = [img.get('src') for img in _dg_images if img.get('src')]
            dg_alts = [img.get('alt') for img in _dg_images if img.get('alt')]
            images.extend(dg_images)
            alts.extend(dg_alts)

        _sl = soup.find('h3', string='Sidelights')
        if _sl:
            _sl = _sl.parent.parent.parent
            _sl_images = _sl.select('.acc-content .door-img img')
            sl_images = [img.get('src') for img in _sl_images if img.get('src')]
            sl_alts = [img.get('alt') for img in _sl_images if img.get('alt')]
            images.extend(sl_images)
            alts.extend(sl_alts)

        data = {
            "title": title,
            "meta_description": meta_description,
            "entry_title": entry_title,
            "images": images,
            "alts": alts,
            "description": description,
            "url": url,
        }
        return data

    def get_urls(self):
        scrapper = create_scraper()
        base = "https://www.odl.com"
        resp = scrapper.get("https://www.odl.com/products")
        soup = BeautifulSoup(markup=resp.text, features="html.parser")
        items = soup.select(".products-items > .product > a.prod-img")
        for item in items:
            href = item.get("href")
            if href:
                href = href.split("?")[0]
                self.urls.append(f"{base}{href}")
