import json
import time
from csv import DictReader
from typing import List

import os
import random
import requests

from core.db_connector import db
from core.models import Business
from core.proxies import proxies
from .helpers import sget, create_url


# 2 - address
# 4[3] - reviews url & count
# 7[2] - website
# 9- lot lan
# 11 - full name
# 13- cathegory
# 18 - name + full address
# 34[1] - hours
# 57 - owner?
# 100[1] - highlights, accecability, etc.
# 157 - logo? image
# 178[3] - phone
# 183[1][3] - city
# 183[1][4] - ZIP
# 183[1][5] - state
# 203[1][4][0] - status
# 72[0][1][6][0] - image


class GmapsApiScrapper:
    def __init__(self, query, region):
        self.source = "gmaps"
        self.project = "encycloweedia"

        self.query = query
        self.cities_coords = self.get_cities_coords(region)
        self.failed = []
        self.api_url = (
            "https://www.google.com/search?tbm=map&authuser=0"
            "&hl=en&gl=by&pb=!4m8!1m3!1d61696.65603528761!2d{}!3d{}!3m2!1i884!2i"
            "754!4f13.1!7i20!8i{}!10b1!12m8!1m1!18b1!2m3!5m1!6e2!20e3!10b1!16b1!"
            "19m4!2m3!1i360!2i120!4i8!20m57!2m2!1i203!2i100!3m2!2i4!5b1!6m6!1m2!"
            "1i86!2i86!1m2!1i408!2i240!7m42!1m3!1e1!2b0!3e3!1m3!1e2!2b1!3e2!1m3!"
            "1e2!2b0!3e3!1m3!1e3!2b0!3e3!1m3!1e8!2b0!3e3!1m3!1e3!2b1!3e2!1m3!1e9"
            "!2b1!3e2!1m3!1e10!2b0!3e3!1m3!1e10!2b1!3e2!1m3!1e10!2b0!3e4!2b1!4b1"
            "!9b0!22m2!1s4XZGX_WrJpCprgTqhK7ADQ!7e81!24m52!1m13!13m6!2b1!3b1!4b1"
            "!6i1!8b1!9b1!18m5!3b1!4b1!5b1!6b1!9b1!2b1!5m5!2b1!3b1!5b1!6b1!7b1!1"
            "0m1!8e3!14m1!3b1!17b1!20m4!1e3!1e6!1e14!1e15!21e2!24b1!25b1!26b1!30"
            "m1!2b1!36b1!43b1!52b1!54m1!1b1!55b1!56m2!1b1!3b1!65m5!3m4!1m3!1m2!1"
            "i224!2i298!26m4!2m3!1i80!2i92!4i8!30m28!1m6!1m2!1i0!2i0!2m2!1i458!2"
            "i754!1m6!1m2!1i834!2i0!2m2!1i884!2i754!1m6!1m2!1i0!2i0!2m2!1i884!2i"
            "20!1m6!1m2!1i0!2i734!2m2!1i884!2i754!34m14!2b1!3b1!4b1!6b1!8m4!1b1!"
            "3b1!4b1!6b1!9b1!12b1!14b1!20b1!23b1!37m1!1e81!49m1!3b1!50m3!2e2!3m1"
            "!3b1!65m0&q={}"
            # &tch=1&ech=1&psi=4XZGX_WrJpCprgTqhK7ADQ.1598453475698.1'
        )

    def start_scrapping(self):
        self.get_data()

    def get_data(self):
        offset_step = 20
        for city_coords in self.cities_coords:
            offset = 0
            while True:
                data_part = self.get_data_part(city_coords, offset)
                print(city_coords["city"], len(data_part), offset)
                offset += offset_step
                if not data_part:
                    break
                for business_data in data_part:
                    source_name__id = business_data["source_name__id"]
                    exists = (
                        Business.query.filter(
                            Business.source_name__id == source_name__id
                        ).scalar()
                        is not None
                    )
                    if exists:
                        business = Business.query.filter(
                            Business.gmaps_id == source_name__id
                        ).first()
                        for key, value in business_data.items():
                            setattr(business, key, value)
                    else:
                        business = Business(**business_data)
                        db.session.add(business)
                db.session.commit()
        self.retry_failed()

    def retry_failed(self):
        self.cities_coords = self.failed
        self.get_data()

    def get_data_part(self, city_coords: dict, offset: int) -> List:
        time.sleep(random.uniform(0.5, 1.5))
        proxy_index = random.randint(0, len(proxies) - 1)
        proxy = {"http": proxies[proxy_index], "https": proxies[proxy_index]}

        city = city_coords["city"]
        lng = city_coords["lng"]
        lat = city_coords["lat"]
        query = self.query

        data = []
        try:
            url = self.api_url.format(lng, lat, offset, f"{query}+{city}")
            resp = requests.get(
                url,
                proxies=proxy
            )
            resp_text_json = resp.text[4:]
            resp_json = json.loads(resp_text_json)
            business_entities = resp_json[0][1][1:]

            for entity in business_entities:
                entity_data = entity[14]
                gmaps_id = entity_data[10]

                _coordinates = sget(entity_data, 9, [])
                lat = sget(_coordinates, 2, "")
                lng = sget(_coordinates, 3, "")

                _website = sget(entity_data, 7, [])
                website = sget(_website, 1, "")

                _phone = sget(entity_data, 178, [])
                _phone = sget(_phone, 0, [])
                phone = sget(_phone, 3, "") or sget(_phone, 0, "")

                _zip = sget(entity_data, 183, [])
                _zip = sget(_zip, 1, [])
                zip_code = sget(_zip, 4, "")

                _country = sget(entity_data, 183, [])
                _country = sget(_country, 1, [])
                country = sget(_country, 6, "")

                _state = sget(entity_data, 183, [])
                _state = sget(_state, 1, [])
                state = sget(_state, 5, "")

                _city = sget(entity_data, 183, [])
                _city = sget(_city, 1, [])
                city = sget(_city, 3, "")

                _status = sget(entity_data, 203, [])
                _status = sget(_status, 1, [])
                _status = sget(_status, 4, [])
                status = sget(_status, 0, "")

                b_hours = {}
                _b_hours = sget(entity_data, 34, [])
                _b_hours = sget(_b_hours, 1, [])

                for _day in _b_hours:
                    day = sget(_day, 0, "")
                    _hours = sget(_day, 1, [])
                    hours = sget(_hours, 0, [])
                    b_hours.update({day: hours})

                item_collected = {
                    "source": self.source,
                    "source_name__id": f"gmaps_{gmaps_id}",
                    "project": self.project,
                    "name": sget(entity_data, 11, ""),
                    "category": sget(sget(entity_data, 13, []), 0, ""),
                    "status": status,
                    "hours": b_hours,
                    "address": sget(entity_data, 18, ""),
                    "city": city,
                    "country": country,
                    "state": state,
                    "zip": zip_code,
                    "phone": phone,
                    "website": website,
                    "lat": lat,
                    "lng": lng,
                }
                data.append(item_collected)
        except Exception as e:
            print(e)
            self.failed.append({"city_coords": city_coords, "offset": offset})

        return data

    @staticmethod
    def get_cities_coords(region: str) -> List:
        result = []
        dir_path = os.path.dirname(os.path.realpath(__file__))
        filename = "worldcities.csv"
        filepath = os.path.join(dir_path, "files", filename)
        with open(filepath, "r") as reader_file:
            reader = DictReader(reader_file)
            for line in reader:
                if region in [
                    line["country"],
                    line["city"],
                    line["city_ascii"],
                    line["iso2"],
                    line["iso3"],
                ]:
                    result.append(
                        {
                            "city": line["city_ascii"],
                            "lat": line["lat"],
                            "lng": line["lng"],
                        }
                    )
        return result
